from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import CustomUser


class CustomObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["mobile_number"] = user.mobile_number
        token["email"] = user.email
        token["custom_user_id"] = user.user_id
        return token


def get_token_pair(user: CustomUser) -> dict:
    """
    Custom extension to the token pair serializer,
    this adds additional manual fields required into the payload
    """
    token = CustomObtainPairSerializer.get_token(user)
    return {"access_token": str(token.access_token), "refresh_token": str(token)}
