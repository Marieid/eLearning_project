import factory
from factory.django import DjangoModelFactory
from ..models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Message, Enrollment, EnrollmentNotification, MaterialNotification
from django.contrib.auth.models import Group
from django.db.models.signals import post_save


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')


class ElearnUserFactory(DjangoModelFactory):
    class Meta:
        model = elearnUser
    user = factory.SubFactory(UserFactory)
    user_type = factory.Iterator(
        elearnUser.USER_TYPE_CHOICES, getter=lambda c: c[0])


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    code = factory.Sequence(lambda n: f'COURSE{n}')
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')
    teacher = factory.SubFactory(ElearnUserFactory, user_type='teacher')
    start_date = factory.Faker('past_date')
    end_date = factory.Faker('future_date')
    # Set default enrollment status to 'open'
    enrollment_status = 'open'


class MaterialFactory(DjangoModelFactory):
    class Meta:
        model = Material

    course = factory.SubFactory(CourseFactory)
    file = factory.django.FileField(filename='test_file.txt')
    uploader = factory.SubFactory(ElearnUserFactory)
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')


class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback
        
    student = factory.SubFactory(ElearnUserFactory, user_type='student')
    course = factory.SubFactory(CourseFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('sentence')


class StatusUpdateFactory(DjangoModelFactory):
    class Meta:
        model = StatusUpdate

    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')


class ChatRoomFactory(DjangoModelFactory):
    class Meta:
        model = ChatRoom

    chat_name = factory.Sequence(lambda n: f'chat_room_{n}')
    admin = factory.SubFactory(UserFactory)


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    chat_room = factory.SubFactory(ChatRoomFactory)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')


class EnrollmentFactory(DjangoModelFactory):
    class Meta:
        model = Enrollment

    student = factory.SubFactory(ElearnUserFactory, user_type='student')
    course = factory.SubFactory(CourseFactory)


# Mute signals to prevent notification creation during testing
@factory.django.mute_signals(post_save)
class EnrollmentNotificationFactory(DjangoModelFactory):
    class Meta:
        model = EnrollmentNotification

    course = factory.SubFactory(CourseFactory)
    student = factory.SubFactory(ElearnUserFactory, user_type='student')
    teacher = factory.SubFactory(ElearnUserFactory, user_type='teacher')


@factory.django.mute_signals(post_save)
class MaterialNotificationFactory(DjangoModelFactory):
    class Meta:
        model = MaterialNotification

    material = factory.SubFactory(MaterialFactory)
    student = factory.SubFactory(ElearnUserFactory, user_type='student')
