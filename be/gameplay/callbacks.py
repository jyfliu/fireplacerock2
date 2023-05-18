class UnrecognizedCommand(BaseException):
  # internal syntax error (shouldn't happen)
  def __init__(self, message=""):
    self.message = message
  def __str__(self):
    return self.message

class InvalidMove(BaseException):
  # illegal move (front end allowed something which shouldnt be allowed)
  def __init__(self, message=""):
    self.message = message
  def __str__(self):
    return self.message

class GameOver(BaseException):
  def __init__(self, winner):
    self.winner = winner
  def __str__(self):
    return f"Player {self.winner} wins! Congratulations!" if self.winner else "Draw"

