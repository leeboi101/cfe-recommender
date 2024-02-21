from faker import Faker 
def get_fake_profiles(count=10):
    fake = Faker()
    user_data = []
    for _ in range(count):
        profile = fake.profile()
        data = {
            "username": profile.get('username'),
            "email": profile.get('email'),
            # code for password: "password": make_password(fake.password(length=15)),
            "is_active": True
        }
        user_data.append(data)
    return(user_data)