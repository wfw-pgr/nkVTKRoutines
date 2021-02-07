import os, sys, vtk
import numpy                  as np
import vtk.util.numpy_support as vtknp

# --------------------------------------------------- #
# --                                               -- #
# -- For Points displaying                         -- #
# --   Data = [nData,nComponents]                  -- #
# --   components = x_,y_,z_,f1_,f2_,....          -- #
# --                                               -- #
# --------------------------------------------------- #

# ========================================================= #
# ===  convert__vtkPolyPoints                           === #
# ========================================================= #

def convert__vtkPolyPoints( Data=None, outFile="out.vtp", DataFormat="binary", names=None ):
    polyData     = vtkPolyPoints( Data=Data, names=names )
    save__vtkPolyPoints( polyData=polyData, outFile=outFile, DataFormat=DataFormat )
    return()


# ========================================================= #
# ===  vtkPolyPoints                                    === #
# ========================================================= #

def vtkPolyPoints( Data=None, names=None ):

    x_,y_,z_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] Define structures                     --- #
    # ------------------------------------------------- #
    # -- [1-1] Data dimension check                 --  #
    if ( Data.ndim != 2 ):
        print( "[vtkPolyPoints] Data's dimension is not 2...   [ERROR]" )
        print( "[vtkPolyPoints] Data :: {0}".format( Data.ndim ) )
        sys.exit()
    nData       = Data.shape[0]
    nComponents = Data.shape[1]
    # -- [1-2] prepare points & lines & coordinates --  #
    coordinates = Data[:,x_:z_+1]
    nScholars   = nComponents - 3
    if ( nScholars >= 1 ):
        scholars    = np.reshape( ( Data[:,z_+1:] ), (-1,nScholars) )
    # -- [1-3] names check                          --  #
    if ( names is None ):
        names = [ "pointData{0:02}".format( ik ) for ik in range( nScholars ) ]
    if ( len( names ) != nScholars ):
        print( "[vtkPolyPoints] len( names ) does not match nScholars..... [ERROR] " )
        print( "[vtkPolyPoints] Data  :: {0} ".format( Data.shape ) )
        print( "[vtkPolyPoints] names :: {0} ".format( names      ) )
        sys.exit()
    
    # ------------------------------------------------- #
    # --- [2] Define Line                           --- #
    # ------------------------------------------------- #
    # -- set vtk poly data -- #
    polyData    = vtk.vtkPolyData()
    pts         = vtk.vtkPoints()
    # coordinates = vtknp.numpy_to_vtk( coordinates, deep=True )
    # pts.SetData( coordinates )
    polyData.SetPoints( pts )
    vertices = vtk.vtkCellArray()

    for ik in range( nData ):
        id = pts.
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(id)
    
    vertices.SetCells( vtk.VTK_POLY_VERTEX, vtknp.numpy_to_vtkIdTypeArray( coordinates, deep=True ) )
    # cell        = np.reshape( np.arange( nData, dtype=np.int64 ), (-1,) )
    # vertices.SetCells( vtk.VTK_POLY_VERTEX, vtknp.numpy_to_vtkIdTypeArray( cell ) )
    # polyData.GetCellData().AddArray( vtknp.numpy_to_vtkIdTypeArray( cell ) )
    polyData.SetVerts( vertices )
    for ik in range( nScholars ):
        hscholar = vtknp.numpy_to_vtk( scholars[:,ik], deep=True, array_type=vtk.VTK_ID_TYPE )
        hscholar.SetName( names[ik] )
        # vertices.SetCells( vtk.VTK_POLY_VERTEX, vtknp.numpy_to_vtkIdTypeArray( cell ) )
    return ( polyData )



# ========================================================= #
# ===  save as XML polyData VTK File                    === #
# ========================================================= #

def save__vtkPolyPoints( polyData=None, DataFormat="binary", outFile="out.vtp" ):

    # ------------------------------------------------- #
    # --- [1] save in vtp File                      --- #
    # ------------------------------------------------- #
    writer = vtk.vtkXMLPolyDataWriter()
    if ( DataFormat.lower() == "ascii"  ):
        writer.SetDataModeToAscii()
    if ( DataFormat.lower() == "binary" ):
        writer.SetDataModeToBinary()
    writer.SetFileName( outFile )
    writer.SetInputData( polyData )
    writer.Write()
    print( "[vtkDataConverter] output :: {0} ".format( outFile ) )
    return()


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    x_,y_,z_,f_  = 0, 1, 2, 3
    outFile      = "out.vtp"
    
    nDiv         = 101
    xpt1         = np.array( [ 0.0, 0.0, 0.0 ] )
    xpt2         = np.array( [ 1.0, 1.0, 1.0 ] )
    points       = np.zeros( (nDiv,4) )
    points[:,x_] = np.linspace( xpt1[x_], xpt2[x_], nDiv )
    points[:,y_] = np.linspace( xpt1[y_], xpt2[y_], nDiv )
    points[:,z_] = np.linspace( xpt1[z_], xpt2[z_], nDiv )
    points[:,f_] = np.linspace( xpt1[x_], xpt2[x_], nDiv )
    convert__vtkPolyPoints( Data=points, outFile=outFile, names=["point01"], DataFormat="ascii" )

