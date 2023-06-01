import random

names = [ # all working cards
  "mew", "unown",
  "sprightelf", # targeting protection not working
  "magikarp", "mudkip", "pikachu", "grovyle", "ampharos",
  "blastoise", "wailord", "snorlax", "garchomp", "jirachi", "hooh",
  # "kyogre", "groudon", "giratina",
  "arceus", "gallade", "heracross", "shuckle", "breloom", "chansey",
  "tyranitar", "gengar", "dragonite",
  # "gyarados"
  "salamence", "lugia", "lapras", "turtwig",
  "sprightjet", "sprightblue", "sprightpixie", "windupkitten",
  "livetwinlilla", "livetwinkisikil", "livetwintroublesunny", "omen",
  # "brimstone", "viper",
  "reyna",
  # "cypher", "neon",
  "jett", "phoenix", "dartmonkey",
  # "supermonkey", "johnnywyles", "riverwyles", "redamogus", "zoe"
  "lopunny", "megalopunny",
  "eevee",
  # Spells
  "ultraball", "repel", "squirtbottle", "technicalmachine", "1tap", "switchout",
  "sprightstarter", "odinspam", "ancientruins",
]

deck1 = random.sample(names, k=16) * 3
deck2 = random.sample(names, k=16) * 3

# structure decks

sd_pote = [
  "dartmonkey", "dartmonkey", "dartmonkey",
  "beedrill", "beedrill", "beedrill",
  "mew", "mew", "mew",
  "shuckle", "shuckle", "shuckle",
  "grovyle", "grovyle", "grovyle",
  "sprightblue", "sprightblue", "sprightblue",
  "sprightjet", "sprightjet", "sprightjet",
  "sprightpixie", "sprightpixie", "sprightpixie",
  "windupkitten",
  "livetwinlilla", "livetwinlilla", "livetwinlilla",
  "livetwinkisikil", "livetwinkisikil", "livetwinkisikil",
  "livetwintroublesunny", "livetwintroublesunny", "livetwintroublesunny",
  "megabracelet", "megabracelet", "megabracelet",
  # "livetwinmoonlitsnitch", "livetwinmoonlitsnitch", "livetwinmoonlitsnitch",
  "squirtbottle", "squirtbottle", "squirtbottle",
]

ed_pote = [
  "megabeedrill", "megabeedrill", "megabeedrill",
  "sprightelf", "sprightelf", "sprightelf",
]

sd_cs = [
  "unown", "unown", "unown",
  "pikachu", "mudkip",
  "lopunny", "lopunny", "lopunny",
  "grovyle", "grovyle",
  "gallade", "heracross",
  "ditto", "ditto", "ditto",
  "eevee", "eevee",
  "ampharos", "ampharos",
  "blastoise", "garchomp",
  "jirachi", "hooh",
  "tyranitar",
  "technicalmachine", "technicalmachine", "technicalmachine",
  "megabracelet", "megabracelet", "megabracelet",
  "pokemonshuffle", "pokemonshuffle", "pokemonshuffle",
]

ed_cs = [
  "megalopunny", "megalopunny", "megalopunny",
  "mew",
  "jirachi",
  "hooh",
  "lugia",
  "arceus",
  "arceus",
  "arceus",
]

