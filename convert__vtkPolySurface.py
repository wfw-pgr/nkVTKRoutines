import os, sys, vtk
import numpy                  as np
import vtk.util.numpy_support as vtknp

# ----------------------------------------- #
# -- Data[ nData, nComponents ]          -- #
# -- components :: x,y,z,f1,f2,f3,...... -- #
# ----------------------------------------- #

# ========================================================= #
# ===  convert__vtkPolySurface                          === #
# ========================================================= #

def convert__vtkPolySurface( Data=None, outFile="out.vtp", names=None, \
                             DataFormat="binary" ):
    polyData     = vtkPolySurface( Data=Data, names=names )
    save__vtkPolySurface( polyData=polyData, outFile=outFile, DataFormat=DataFormat )
    return()


# ========================================================= #
# ===  vtkPolySurface                                   === #
# ========================================================= #

def vtkPolySurface( Data=None, names=None ):

    x_,y_,z_ = 0, 1, 2
    # ------------------------------------------------- #
    # --- [1] Arguments Check                       --- #
    # ------------------------------------------------- #
    if ( Data is None ): sys.exit( "[vtkPolySurface] Data == ???" )
    nComponents  = Data.shape[1]
    if ( nComponents == 3 ):
        coordinates = np.copy( Data[:,x_:z_+1] )
        scholars    = np.reshape( Data[:,z_], (Data.shape[0],1) )
    if ( nComponents >= 4 ):
        coordinates = np.copy( Data[:,x_:z_+1] )
        scholars    = np.copy( Data[:,z_+1:  ] )
    nScholars = scholars.shape[1]
    if ( names is None ):
        names = [ "Data{0:02}".format(ik+1) for ik in range( nScholars ) ]
    if ( len( names ) != nScholars ):
        print( "[convert__vtkPolySurface] unmatched names & Data size .... [ERROR] " )
        print( "[convert__vtkPolySurface] Data size :: {0} ".format( Data.shape )    )
        print( "[convert__vtkPolySurface] names     :: {0} ".format( names      )    )
        
    # ------------------------------------------------- #
    # --- [2] Coordinates Points Settings           --- #
    # ------------------------------------------------- #
    #  -- [2-1] Coordinates Points                  --  #
    coordinates_ = vtknp.numpy_to_vtk( coordinates, deep=True )
    points       = vtk.vtkPoints()
    points.SetData( coordinates_ )
    #  -- [2-2] define PolyData / CellDataArray     --  #
    polyData     = vtk.vtkPolyData()
    polyData.SetPoints( points )
    cellArray    = vtk.vtkCellArray()
    #  -- [2-3] assign pointData to polyData        --  #
    for ik in range( nScholars ):
        pointData_   = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
        pointData_.SetName( names[ik] )
        polyData.GetPointData().AddArray( pointData_ )
    #  -- [2-4] boundary for Delaunay2D             --  #
    boundary     = vtk.vtkPolyData()
    boundary.SetPoints( polyData.GetPoints() )
    boundary.SetPolys ( cellArray )
    # ------------------------------------------------- #
    # --- [3] Delaunay triangulation                --- #
    # ------------------------------------------------- #
    delaunay   = vtk.vtkDelaunay2D()
    delaunay.SetInputData ( polyData )
    delaunay.SetSourceData( boundary  )
    delaunay.Update()

    # ------------------------------------------------- #
    # --- [4] return polyData                       --- #
    # ------------------------------------------------- #
    return( delaunay.GetOutput() )

    
    
# ========================================================= #
# ===  save as XML polyData VTK File                    === #
# ========================================================= #

def save__vtkPolySurface( polyData=None, DataFormat="binary", outFile="out.vtp" ):

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
    print( "[save__vtkPolySurface] output :: {0} ".format( outFile ) )
    return()


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    x_,y_,z_,f_     = 0, 1, 2, 3
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum     = [ -1.0, 1.0, 21 ]
    x2MinMaxNum     = [ -1.0, 1.0, 21 ]
    x3MinMaxNum     = [  0.0, 0.0,  1 ]
    ret             = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                         x3MinMaxNum=x3MinMaxNum, returnType = "point"     )
    ret[:,z_]       = np.exp( - 0.50 * ( ret[:,x_]**2 + ret[:,y_]**2 )  )
    Data            = np.zeros( (ret.shape[0],4) )
    Data[:,x_:z_+1] = ret[:,x_:z_+1]
    Data[:,f_]      = np.sqrt( ret[:,x_]**2 + ret[:,y_]**2 )

    convert__vtkPolySurface( Data=Data )
    
