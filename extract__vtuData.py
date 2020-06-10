import vtk
import numpy                  as np
import vtk.util.numpy_support as nps


# ========================================================= #
# ===  extract__vtuData                                 === #
# ========================================================= #

def extract__vtuData( inpFile=None, key=None, coord=None ):

    # ------------------------------------------------- #
    # --- [1] Read vtu File                         --- #
    # ------------------------------------------------- #
    
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName( inpFile )
    reader.Update()

    # ------------------------------------------------- #
    # --- [2] import points to be interpolated      --- #
    # ------------------------------------------------- #
    
    coordinates = nps.numpy_to_vtk( coord, deep=True )
    points      = vtk.vtkPoints()
    points.SetData( coordinates )
    
    profile     = vtk.vtkPolyData()
    profile.SetPoints( points )

    # ------------------------------------------------- #
    # --- [3] probing Data                          --- #
    # ------------------------------------------------- #

    probe = vtk.vtkProbeFilter()
    probe.SetInputData( profile )
    probe.SetSourceConnection( reader.GetOutputPort() )
    probe.Update()
    
    Data  = nps.vtk_to_numpy( probe.GetOutput().GetPointData().GetArray(key) )
    ret   = np.concatenate( [ coord, Data ], axis=-1 )
    return( ret )

    
# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    
    inpFile     = "vtu/cShape_magnet_t0001.vtu"
    key         = "magnetic field strength e"
    
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ -1.0, +1.0, 301 ]
    x2MinMaxNum = [  0.0, +0.0,   1 ]
    x3MinMaxNum = [ -1.0, +1.0, 301 ]
    coord       = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "point" )
    ret         = extract__vtuData( inpFile=inpFile, key=key, coord=coord )
    
    pngFile     = "out.png"
    import nkUtilities.cMapTri as cmt
    cmt.cMapTri( xAxis=ret[:,0], yAxis=ret[:,2], cMap=ret[:,5], pngFile=pngFile )
    print( ret )
