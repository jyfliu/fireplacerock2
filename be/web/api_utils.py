
def serialize_template(template):
    if template is None:
        return None
    dict = {}
    dict["name"] = template.name
    dict["cost"] = template.cost
    dict["type"] = template.type
    if template.type == "monster":
        dict["attack"] = template.attack
        dict["health"] = template.health
    dict["template_id"] = template.id

    dict["description"] = template.description
    dict["flavour"] = template.flavour

    if template.sprite:
      dict["sprite"] = template.sprite
    if template.mini_sprite:
      dict["mini_sprite"] = template.mini_sprite
    dict["bkgd_colour"] = template.bkgd_colour

    return dict


def serialize_card(card, sprite_cache):
    if card is None:
      return None
    dict = {}
    dict["name"] = card.name
    dict["cost"] = card.cost
    dict["type"] = card.type
    if card.type == "monster":
      dict["attack"] = card.attack
      dict["health"] = card.health
      dict["original_attack"] = card.original_attack
      dict["original_health"] = card.original_health
    dict["uuid"] = card.uuid
    dict["template_id"] = card.id

    dict["can_activate"] = card.can("activate")
    dict["can_activate_hand"] = card.can("activate_hand")
    dict["can_attack"] = card.can("attack")
    dict["can_attack_directly"] = card.can("attack_directly")
    dict["can_summon"] = card.can("summon")
    dict["can_summon_extradeck"] = card.can("summon_extradeck")

    dict["description"] = card.template.description
    dict["flavour"] = card.template.flavour

    if card.uuid not in sprite_cache and card.template.sprite:
      dict["sprite"] = card.template.sprite
    if card.uuid not in sprite_cache and card.template.mini_sprite:
      dict["mini_sprite"] = card.template.mini_sprite
    dict["bkgd_colour"] = card.template.bkgd_colour

    return dict