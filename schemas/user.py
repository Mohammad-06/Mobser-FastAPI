from pydantic import BaseModel, EmailStr, field_validator
import html
import re


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        if not v:
            return v

        v = html.escape(v)
        v = re.sub(r"[<>{}]", '', v)
        v = v.strip()

        if len(v) > 100:
            v = v[:100]
        return v

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        if not v:
            raise ValueError("Email cannot be empty")


        v = html.escape(v)
        v = re.sub(r"[<>{}]", '', v)
        v = v.strip().lower()


        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Invalid email format")

        if len(v) > 254:
            v = v[:254]

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("Password cannot be empty")

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")

        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")

        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def sanitize_login_email(cls, v: str) -> str:
        if not v:
            raise ValueError("Email cannot be empty")

        v = html.escape(v)
        v = re.sub(r"[<>{}]", '', v)
        v = v.strip().lower()
        return v

    @field_validator('password')
    @classmethod
    def ensure_string_password(cls, v):
        if isinstance(v, list):
            return str(v[0]) if v else ""
        return str(v)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool

    @field_validator("name")
    @classmethod
    def escape_name_output(cls, v: str) -> str:
        return html.escape(v)

    @field_validator("email")
    @classmethod
    def escape_email_output(cls, v: str) -> str:
        return html.escape(v)

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None

    @field_validator("name")
    @classmethod
    def sanitize_update_name(cls, v: str | None) -> str | None:
        if not v:
            return v

        v = html.escape(v)
        v = re.sub(r"[<>{}]", '', v)
        v = v.strip()

        if len(v) > 100:
            v = v[:100]
        return v

    @field_validator("email")
    @classmethod
    def sanitize_update_email(cls, v: str | None) -> str | None:
        if not v:
            return v

        v = html.escape(v)
        v = re.sub(r"[<>{}]", '', v)
        v = v.strip().lower()

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Invalid email format")

        if len(v) > 254:
            v = v[:254]

        return v

    @field_validator("password")
    @classmethod
    def validate_update_password(cls, v: str | None) -> str | None:
        if not v:
            return v

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")

        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")

        return v