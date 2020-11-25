import os, sys, vtk
import numpy                  as np
import vtk.util.numpy_support as vtknp

# ----------------------------------------- #
# -- Data[nData,nComponents ]            -- #
# -- components :: x,y,z,f1,f2,f3,...... -- #
# ----------------------------------------- #

# ========================================================= #
# ===  convert__vtkUnstructuredGrid                     === #
# ========================================================= #

def convert__vtkUnstructuredGrid( Data=None, outFile="out.vtu", names=None, shape=None, \
                                  DataFormat="binary" ):
    
    # ------------------------------------------------- #
    # --- [1] Data empty check                      --- #
    # ------------------------------------------------- #
    if ( Data is None ):
        sys.exit( "[vtkUnstructuredGrid] Data == ???" )
    # ------------------------------------------------- #
    # --- [2] Data reshaping                        --- #
    # ------------------------------------------------- #
    if ( shape is not None ):
        Data_ = np.reshape( Data, shape )
    else:
        Data_ = np.copy   ( Data )
    # ------------------------------------------------- #
    # --- [3] convert into structured Grid Data     --- #
    # ------------------------------------------------- #
    if   ( Data_.ndim == 2 ):
        unstructData = vtkUnstructuredGrid3d( Data=Data_, names=names )
    else:
        print( "[convert__vtkUnstructuredGrid] Data dimension is not [ 2 ] " )
        print( "[convert__vtkUnstructuredGrid] Data shape :: [nData,nComponents] " )
        print( "[convert__vtkUnstructuredGrid] Data.ndim  :: {0} ".format( Data_.ndim ) )
        sys.exit()
    # ------------------------------------------------- #
    # --- [4] write structured Grid Data            --- #
    # ------------------------------------------------- #
    save__vtkUnstructuredGrid( unstructData=unstructData, outFile=outFile, DataFormat=DataFormat )
    return()



# ========================================================= #
# ===  vtkUnstructuredGrid3d                            === #
# ========================================================= #

def vtkUnstructuredGrid3d( Data=None, names=None ):

    x_,y_,z_ = 0, 1, 2
    # ------------------------------------------------- #
    # --- [1] Arguments Check                       --- #
    # ------------------------------------------------- #
    if ( Data is None ):
        sys.exit( "[vtkUnstructuredGrid] Data == ???" )
    # ------------------------------------------------- #
    # --- [2] Data size check                       --- #
    # ------------------------------------------------- #
    #  -- [2-2] nComponents check                   --  #
    nComponents  = Data.shape[1]
    if   ( nComponents == 3 ):
        coordinates = np.reshape( Data[:,x_:z_+1], (-1,3) )
        scholars    = np.reshape( Data[:,x_:z_+1], (-1,3) )
    elif ( nComponents >= 4 ):
        coordinates = np.reshape( Data[:,x_:z_+1], (-1,3) )
        scholars    = np.reshape( Data[:,z_+1:  ], (-1,nComponents-3) )
    #  -- [2-3] nScholars check                     --  #
    nScholars = scholars.shape[1]

    # ------------------------------------------------- #
    # --- [3] naming                                --- #
    # ------------------------------------------------- #
    if ( names is None ):
        names = [ "Data{0:02}".format(ik+1) for ik in range( nScholars ) ]
    if ( len( names ) != nScholars ):
        print( "[convert__vtkUnstructuredGrid] unmatched names & Data size .... [ERROR] " )
        print( "[convert__vtkUnstructuredGrid] Data size :: {0} ".format( Data.shape )    )
        print( "[convert__vtkUnstructuredGrid] names     :: {0} ".format( names      )    )
        
    # ------------------------------------------------- #
    # --- [4] Coordinates Points Settings           --- #
    # ------------------------------------------------- #
    #  -- [4-1] Coordinates Points                  --  #
    coordinates_ = vtknp.numpy_to_vtk( coordinates, deep=True )
    points       = vtk.vtkPoints()
    points.SetData( coordinates_ )
    #  -- [4-2] define unstructData / CellDataArray   --  #
    unstructData = vtk.vtkUnstructuredGrid()
    unstructData.SetPoints( points )
    #  -- [4-3] assign pointData to unstructData      --  #
    for ik in range( nScholars ):
        pointData_   = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
        pointData_.SetName( names[ik] )
        unstructData.GetPointData().AddArray( pointData_ )
    #  -- [4-4] Delaunay triangulation                --  #
    delaunay     = vtk.vtkDelaunay3D()
    delaunay.SetInputData( unstructData )
    delaunay.BoundingTriangulationOff()
    delaunay.Update()
    ret          = delaunay.GetOutput()

    # ------------------------------------------------- #
    # --- [5] return unstructData                     --- #
    # ------------------------------------------------- #
    return( ret )


    
# ========================================================= #
# ===  save as XML polyData VTK File                    === #
# ========================================================= #

def save__vtkUnstructuredGrid( unstructData=None, DataFormat="binary", outFile="out.vtp" ):

    # ------------------------------------------------- #
    # --- [1] save in vtp File                      --- #
    # ------------------------------------------------- #
    writer = vtk.vtkXMLUnstructuredGridWriter()
    if ( DataFormat.lower() == "ascii"  ):
        writer.SetDataModeToAscii()
    if ( DataFormat.lower() == "binary" ):
        writer.SetDataModeToBinary()
    writer.SetFileName( outFile )
    writer.SetInputData( unstructData )
    writer.Write()
    print( "[save__vtkUnstructuredGrid] output :: {0} ".format( outFile ) )
    return()



# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    x_,y_,z_,f_       = 0, 1, 2, 3
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum       = [ -1.0, 1.0, 41 ]
    x2MinMaxNum       = [ -1.0, 1.0, 31 ]
    x3MinMaxNum       = [ -1.0, 1.0, 21 ]
    ret               = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                           x3MinMaxNum=x3MinMaxNum, returnType = "point" )
    Data              = np.zeros( (ret.shape[0],5) )
    Data[:,x_:z_+1]   = ret[:,x_:z_+1]
    Data[:,f_]        = np.sqrt( ret[:,x_]**2 + ret[:,y_]**2 )
    Data[:,4 ]        = np.exp ( -0.5 * ( ret[:,x_]**2 + ret[:,y_]**2 ) )

    convert__vtkUnstructuredGrid( Data=Data )
