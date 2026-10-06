from pydantic import BaseModel, Field, field_validator

from app.services.gold import (
    GOLD_POSITIONS,
    MAX_GOLD_BASE,
    MAX_GOLD_MODIFIER,
    GoldRules,
)


class GoldRulesData(BaseModel):
    # Oro per gara: base a tutti gli iscritti, modificatori per le posizioni 1-6 e uno
    # unico (other) per tutte le successive. I modificatori possono essere negativi.
    base: int = Field(ge=0, le=MAX_GOLD_BASE)
    positions: list[int] = Field(min_length=GOLD_POSITIONS, max_length=GOLD_POSITIONS)
    other: int = Field(ge=-MAX_GOLD_MODIFIER, le=MAX_GOLD_MODIFIER)

    @field_validator("positions")
    @classmethod
    def check_positions(cls, values: list[int]) -> list[int]:
        if any(abs(value) > MAX_GOLD_MODIFIER for value in values):
            raise ValueError(f"Ogni modificatore deve essere tra -{MAX_GOLD_MODIFIER} e {MAX_GOLD_MODIFIER}")
        return values

    @classmethod
    def from_rules(cls, rules: GoldRules) -> "GoldRulesData":
        return cls(base=rules.base, positions=list(rules.positions), other=rules.other)

    def to_rules(self) -> GoldRules:
        return GoldRules(base=self.base, positions=tuple(self.positions), other=self.other)
