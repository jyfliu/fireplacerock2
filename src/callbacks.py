class InvalidMove(BaseException):
  def __init__(self, message=""):
    self.message = message
  def __str__(self):
    return self.message

class GameOver(BaseException):
  def __init__(self, winner):
    self.winner = winner
  def __str__(self):
    return f"Winner: {self.winner}" if self.winner else "Draw"


