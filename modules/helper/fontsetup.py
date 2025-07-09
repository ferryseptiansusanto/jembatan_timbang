from PyQt5.QtCore import Qt

def SetupEdLineFont(edtLine, alignment, fontSize=10, isBold=True ):
    edtLine.setAlignment(alignment)
    font = edtLine.font()
    font.setPointSize(fontSize)
    font.setBold(isBold)
    edtLine.setFont(font)

