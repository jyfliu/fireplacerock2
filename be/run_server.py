import web.server
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument("--prod", action="store_true")
  args = parser.parse_args()

  web.server.run(debug=not args.prod)

