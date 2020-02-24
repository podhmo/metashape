from typing import List


class Data:
    abilities: List['Ability']
    base_experience: int
    forms: List['Ability_Form_Item_Move_Species_Stat_Type_Version']
    game_indices: List['GameIndex']
    height: int
    held_items: List['HeldItem']
    id: int
    is_default: bool
    location_area_encounters: str
    moves: List['Move']
    name: str
    order: int
    species: 'Ability_Form_Item_Move_Species_Stat_Type_Version'
    sprites: 'Sprite'
    stats: List['Stat']
    types: List['Type']
    weight: int


class Ability:
    ability: 'Ability_Form_Item_Move_Species_Stat_Type_Version'
    is_hidden: bool
    slot: int


class GameIndex:
    game_index: int
    version: 'Ability_Form_Item_Move_Species_Stat_Type_Version'


class HeldItem:
    item: 'Ability_Form_Item_Move_Species_Stat_Type_Version'
    version_details: List['VersionDetail']


class VersionDetail:
    rarity: int
    version: 'Ability_Form_Item_Move_Species_Stat_Type_Version'


class Move:
    move: 'Ability_Form_Item_Move_Species_Stat_Type_Version'
    version_group_details: List['VersionGroupDetail']


class VersionGroupDetail:
    level_learned_at: int
    move_learn_method: 'Ability_Form_Item_Move_Species_Stat_Type_Version'
    version_group: 'Ability_Form_Item_Move_Species_Stat_Type_Version'


class Sprite:
    back_default: str
    back_female: None
    back_shiny: str
    back_shiny_female: None
    front_default: str
    front_female: None
    front_shiny: str
    front_shiny_female: None


class Stat:
    base_stat: int
    effort: int
    stat: 'Ability_Form_Item_Move_Species_Stat_Type_Version'


class Type:
    slot: int
    type: 'Ability_Form_Item_Move_Species_Stat_Type_Version'


class Ability_Form_Item_Move_Species_Stat_Type_Version:
    name: str
    url: str


