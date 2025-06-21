from pydantic import BaseModel, EmailStr


class AdminLoginSchema(BaseModel):
    email: EmailStr
    password: str


class ProductNameChangeSchema(BaseModel):
    name: str


class ProductKindChangeSchema(BaseModel):
    kind: str


class ProductPriceChangeSchema(BaseModel):
    price: float


class ProductCategoryChangeSchema(BaseModel):
    category: str


class AdminPasswordRecover(BaseModel):
    code: str
    new_password: str
