
tal = 10
smean = 10


p = MixedIntegerLinearProgram()
w = p.new_variable(integer=True, nonnegative=True)
p.add_constraint(411*w[0] + 295*w[1] + 161*w[2] == 3200)
a = p.polyhedron().integral_points()
