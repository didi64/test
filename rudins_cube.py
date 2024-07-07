import numpy as np
from itertools import combinations, pairwise
import Part
from FreeCAD import Vector

cyclic = lambda pts: zip(pts, np.roll(pts, -1, axis=0))


def make_face(fpts):
    fpts = [Vector(x) for x in fpts]
    poly = Part.makePolygon(fpts + fpts[:1])
    face = Part.Face(poly)
    return face


def make_solid(faces):
    faces_ = [make_face(face) for face in faces]
    shell = Part.makeShell(faces_)
    solid = Part.makeSolid(shell)
    return solid


def make_prism(pts):
    bot, top = pts
    sides = [(a, b, d, c) for (a, b), (c, d) in zip(cyclic(bot), cyclic(top))]
    solid = make_solid([bot, top] + sides)
    return solid


def get_quads():
    e1, e2, e3 = np.eye(3)
    R120 = np.array((e2, e3, e1)).T

    a = 10*2**0.5
    h = 60

    square = np.array([(0, a, 0), (0, 0, a), (0, -a, 0), (0, 0, -a)])
    top = square + h/2*e1
    bot = square - h/2*e1

    el = np.array((bot, top)).reshape((2, -1, 3))
    els = [(el + s*a*e2) @ np.linalg.matrix_power(R120, i).T for i in range(3) for s in (1, -1)]
    quads = [make_prism(el) for el in els]
    return quads


def cut_quads(quads):
    qquads = [quads[2*i:2*i+2] for i in range(3)]
    cuts = [y.cut(xs) for xs, ys in pairwise(qquads + qquads[:1]) for y in ys]
    return cuts


def show_quads():
    for q in get_quads():
        Part.show(q)


def show_cuts():
    for q in cut_quads(get_quads()):
        Part.show(q)
