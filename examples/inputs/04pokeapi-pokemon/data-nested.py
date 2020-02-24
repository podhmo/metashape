from typing import List


class Data:
    class Ability_Form_Item_Move_Species_Stat_Type_Version:
        name: str
        url: str

    class Ability:
        ability: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
        is_hidden: bool
        slot: int

    class GameIndex:
        game_index: int
        version: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'

    class HeldItem:
        class VersionDetail:
            rarity: int
            version: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
    
        item: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
        version_details: List['VersionDetail']

    class Move:
        class VersionGroupDetail:
            level_learned_at: int
            move_learn_method: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
            version_group: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
    
        move: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
        version_group_details: List['VersionGroupDetail']

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
        stat: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'

    class Type:
        slot: int
        type: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'

    abilities: List['Ability']
    base_experience: int
    forms: List['Data.Ability_Form_Item_Move_Species_Stat_Type_Version']
    game_indices: List['GameIndex']
    height: int
    held_items: List['HeldItem']
    id: int
    is_default: bool
    location_area_encounters: str
    moves: List['Move']
    name: str
    order: int
    species: 'Data.Ability_Form_Item_Move_Species_Stat_Type_Version'
    sprites: 'Sprite'
    stats: List['Stat']
    types: List['Type']
    weight: int


