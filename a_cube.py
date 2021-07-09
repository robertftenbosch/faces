from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import itertools

app = QApplication.instance()
if app is None:
    app = QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
w.show()
w.setWindowTitle('A cube')

vertexes = np.array(list(itertools.product(range(2),repeat=3)))

faces = []

for i in range(2):
    temp = np.where(vertexes==i)
    for j in range(3):
        temp2 = temp[0][np.where(temp[1]==j)]
        for k in range(2):
            faces.append([temp2[0],temp2[1+k],temp2[3]])

faces = np.array(faces)

colors = np.array([[1,0,0,1] for i in range(12)])


cube = gl.GLMeshItem(vertexes=vertexes, faces=faces, faceColors=colors,
                     drawEdges=True, edgeColor=(0, 0, 0, 1))

w.addItem(cube)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
        #divide by zero fix
        # if self._vertexNormals is None:
        #     faceNorms = self.faceNormals()
        #     vertFaces = self.vertexFaces()
        #     self._vertexNormals = np.empty(self._vertexes.shape, dtype=float)
        #     for vindex in xrange(self._vertexes.shape[0]):
        #         faces = vertFaces[vindex]
        #         if len(faces) == 0:
        #             self._vertexNormals[vindex] = (0, 0, 0)
        #             continue
        #         norms = faceNorms[faces]  ## get all face normals
        #         norm = norms.sum(axis=0)  ## sum normals
        #         if all(norm == 0):
        #             self._vertexNormals[vindex] = norm
        #             continue
        #         # norm /= (norm**2).sum()**0.5  ## and re-normalize
        #         np.true_divide(norm, (norm ** 2).sum() ** 0.5, out=norm, casting='unsafe')
        #         self._vertexNormals[vindex] = norm