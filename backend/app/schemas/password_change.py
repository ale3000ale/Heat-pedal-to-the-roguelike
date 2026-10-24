"""Contratto riservato al cambio password del proprio account."""
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


class ChangePasswordRequest(BaseModel):
    """Valida tre segreti senza normalizzare spazi o caratteri.

    La nuova password mantiene i limiti della registrazione (8-128).
    Il chiamante HTTP traduce gli errori in un messaggio privo di input.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    current_password: SecretStr = Field(min_length=1, max_length=128)
    new_password: SecretStr = Field(min_length=8, max_length=128)
    confirm_password: SecretStr = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def matching_passwords(self) -> Self:
        """Restituisce il DTO; ValueError se la conferma non coincide."""
        if self.new_password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("La conferma della nuova password non coincide")
        return self
