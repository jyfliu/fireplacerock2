import random

names = [ # all working cards
  "mew", "unown",
  "sprightelf", # targeting protection not working
  "magikarp", "mudkip", "pikachu", "grovyle", "ampharos",
  "blastoise", "wailord", "snorlax", "garchomp", "jirachi", "hooh",
  "beedrill", "scizor", "kangaskhan",
  "kyogre", "groudon", "giratina", "arceus",
  "gallade", "heracross", "shuckle", "breloom", "chansey",
  "tyranitar", "gengar", "dragonite",
  "gyarados",
  "salamence", "lugia", "lapras", "turtwig",
  "sprightjet", "sprightblue", "sprightpixie", "windupkitten",
  "twinlatias", "twinlatios", "twinslatioslatias", "omen",
  "brimstone", "viper", "reyna", "kiljoy",
  "cypher", # "neon",
  "jett", "phoenix",
  "dartmonkey",
  # "supermonkey", "johnnywyles", "riverwyles", "redamogus", "zoe"
  "lopunny",
  "eevee",
  # Spells
  "ultraball", "repel", "squirtbottle", "technicalmachine", "1tap", "switchout",
  "pokemonsafari", "lavendertown", "ancientruins",
  "sprightstarter",
  "odinspam", "shortyangle", "cloudburst",
]

ed_names = [
  "megascizor", "megalopunny", "megabeedrill", "megaheracross",
  "megakangaskhan"
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
  "twinlatias", "twinlatias", "twinlatias",
  "twinlatios", "twinlatios", "twinlatios",
  "twinslatioslatias", "twinslatioslatias", "twinslatioslatias",
  "megabracelet", "megabracelet", "megabracelet",
  # "livetwinmoonlitsnitch", "livetwinmoonlitsnitch", "livetwinmoonlitsnitch",
  "squirtbottle", "squirtbottle", "squirtbottle",
]

ed_pote = [
  "megabeedrill", "megabeedrill", "megabeedrill",
  "sprightelf", "sprightelf", "sprightelf",
]

sd_cs = [
  "pikachu", "mudkip",
  "lopunny", "lopunny", "lopunny",
  "grovyle", "turtwig",
  "gallade", "heracross",
  "ditto",
  "eevee", "eevee",
  "ampharos", "scizor", "lapras", "gengar",
  "blastoise", "garchomp",
  "jirachi", "hooh", "lugia",
  "dragonite", "tyranitar", "salamence",
  "technicalmachine", "technicalmachine", "technicalmachine",
  "megabracelet", "megabracelet", "megabracelet",
  "pokemonshuffle", "pokemonshuffle",
  "pokemonsafari", "pokemonsafari", "pokemonsafari",
]

ed_cs = [
  "megalopunny", "megalopunny", "megalopunny",
  "mew",
  "jirachi",
  "hooh",
  "lugia",
  "giratina",
  "arceus",
  "arceus",
  "arceus",
]


sd_sv = [
  "kiljoy", "kiljoy", "kiljoy",
  "viper", "viper", "viper",
  "reyna", "reyna", "reyna",
  "omen", "omen",
  "cypher", "cypher", "cypher",
  "megabracelet", "megabracelet", "megabracelet",
  "mewtwo", "mewtwo", "mewtwo",
  "dartmonkey", "dartmonkey",
  "supermonkeyfanclub", "supermonkeyfanclub",
  "supermonkey", "supermonkey", "supermonkey",
  "sprightblue", "sprightblue", "sprightblue",
  "twinlatias", "twinlatias", "twinlatias",
  "twinlatios", "twinlatios", "twinlatios",
  "twinslatioslatias", "twinslatioslatias", "twinslatioslatias",
  "odinspam", "cloudburst",
  "shortyangle", "shortyangle", "shortyangle",
]

ed_sv = [
  "megamewtwox", "megamewtwox", "megamewtwox",
  "megamewtwoy", "megamewtwoy", "megamewtwoy",
  "sprightelf", "sprightelf", "sprightelf",
]

