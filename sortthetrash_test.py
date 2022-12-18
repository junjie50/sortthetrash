import sortthetrash as app

class Utility_testing():
  '''Testing for the utility class.'''
  def __init__(self):
    self.join_class_path_test()
    self.password_hash_test()

  def join_class_path_test(self):
    '''Testing for macos'''
    assert(app.Utility.join_class_path("imgs", "test1.png") == "imgs/test1.png")
    assert(app.Utility.join_class_path("imgs", "test2.png") != "imgs/test1.png")
    assert(app.Utility.join_class_path("imgs", "metal", "metal1.png") == "imgs/metal/metal1.png")
  
  def password_hash_test(self):
    password1 = "testing1234"
    password2 = "testing1234"
    diffpass = "differentPass"
    func = app.Utility.password_hash
    assert(func(password1) == func(password2))
    assert(func(password2) != func(diffpass))
    assert(func(password1) != func(diffpass))


if __name__ == "__main__":
  Utility_testing()