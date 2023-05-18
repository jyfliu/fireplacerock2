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
  # Spells
  "squirtbottle", "technicalmachine", "1tap", "switchout"
]

deck1 = random.sample(names, k=16) * 3
deck2 = random.sample(names, k=16) * 3
