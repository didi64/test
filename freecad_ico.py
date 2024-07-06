import numpy as np
import Part
from itertools import combinations, product
from FreeCAD import Vector

norm = np.linalg.norm


def dist(pt0, pts):
    return min(norm(pt-pt0) for pt in pts)


def on_sphere(center, r, pts, eps=0.1):
    return [pt for pt in pts if abs(r-norm(pt-center)) < eps]


def closest(pt0, pts, idxs=None):
    idxs = idxs or range(len(pts))
    return min((norm(pt0-pts[i]), i) for i in idxs)[1]


def sort_pts(pts):
    idxs = set(range(len(pts)))
    i = idxs.pop()
    res = [pts[i]]
    while idxs:
        i = closest(pts[i], pts, idxs)
        res.append(pts[i])
        idxs.remove(i)
    return res


def make_face(fpts):
    poly = Part.makePolygon(fpts + fpts[:1])
    face = Part.Face(poly)
    return face


def make_dual_face(pt, pts):
    r = dist(pt, pts)
    fpts_ = on_sphere(pt, r, pts)
    fpts = sort_pts(fpts_)
    face = make_face(fpts)
    return face


def make_dual_shell(ipts, pts):
    faces = [make_dual_face(pt, pts) for pt in ipts]
    shell = Part.makeShell(faces)
    return shell


def dual_shell(shell):
    pts = [f.CenterOfMass for f in shell.Faces]
    ipts = [v.Point for v in shell.Vertexes]
    dual = make_dual_shell(ipts, pts)
    Part.show(dual)
    return dual


def shape_from_selection():
    return Gui.Selection.getSelection()[0].Shape


def icosaeder(scale=10, eps=0.1):
    R120 = np.roll(np.eye(3), 1, 0)  # rotate 120 degree around (1, 1, 1)
    phi = (1 + np.sqrt(5)) / 2
    pts = [Vector(scale*np.linalg.matrix_power(R120, i) @ (j, k*phi, 0))
                    for i, j, k in product((0, 1, 2), (1, -1), (1, -1))]
    is_edge = lambda p, q: abs((norm(p - q) - 2*scale)) < eps
    is_face = lambda fpts: all(is_edge(p, q) for p, q in combinations(fpts, 2))
    faces = [fpts for fpts in combinations(pts, 3) if is_face(fpts)]
    shell = Part.makeShell([make_face(fpts) for fpts in faces])
    Part.show(shell)
    return shell
