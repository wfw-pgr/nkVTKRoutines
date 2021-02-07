import vtk
import numpy as np
import vtk.util.numpy_support as vtknp


# ========================================================= #
# ===  scatter__vtkPoint                                === #
# ========================================================= #
def scatter__vtkPoint( Data=None, DataFormat="binary", vtkFile="out.vtu" ):

    # ------------------------------------------------- #
    # --- [1] call functions                        --- #
    # ------------------------------------------------- #
    uGrid = convert__point2ugrid( Data )
    save__uGrid( uGrid=uGrid, DataFormat=DataFormat, vtkFile=vtkFile )


# ========================================================= #
# ===  convert__point2ugrid                             === #
# ========================================================= #
def convert__point2ugrid( Data=None, names=None ):

    x_, y_, z_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] preparation                           --- #
    # ------------------------------------------------- #
    if vtk.VTK_ID_TYPE == 12:
        ID_TYPE = np.int64
    else:
        ID_TYPE = np.int32

    #  -- [1-2] nComponents check                   --  #
    nData        = Data.shape[0]
    nComponents  = Data.shape[1]
    if   ( nComponents == 3 ):
        coordinates = np.reshape( Data[:,x_:z_+1], (-1,3) )
        scholars    = np.reshape( Data[:,x_:z_+1], (-1,3) )
    elif ( nComponents >= 4 ):
        coordinates = np.reshape( Data[:,x_:z_+1], (-1,3) )
        scholars    = np.reshape( Data[:,z_+1:  ], (-1,nComponents-3) )
    #  -- [1-3] nScholars check                     --  #
    nScholars = scholars.shape[1]
    #  -- [1-4] names                               --  #
    if ( names is None ):
        names = [ "Data{0:02}".format(ik+1) for ik in range( nScholars ) ]

    
    # ------------------------------------------------- #
    # --- [2] points settings                       --- #
    # ------------------------------------------------- #
    points = vtk.vtkPoints()
    points.SetData( vtknp.numpy_to_vtk( coordinates, deep=True ) )

    # ------------------------------------------------- #
    # --- [3] cell type                             --- #
    # ------------------------------------------------- #
    cell_type = np.full( ( nData,), vtk.VTK_VERTEX )
    cell_type = cell_type.astype( np.uint8 )
    cell_type = vtknp.numpy_to_vtk( cell_type )

    # ------------------------------------------------- #
    # --- [4] offset                                --- #
    # ------------------------------------------------- #
    offset       = np.arange( nData )
    offset       = vtknp.numpy_to_vtkIdTypeArray( ( offset ).astype( ID_TYPE ) )

    # ------------------------------------------------- #
    # --- [5] cell array                            --- #
    # ------------------------------------------------- #
    cell_index   = np.arange( nData  , dtype=np.int64 )
    nVertArray   = np.ones(  (nData,), dtype=np.int64 )
    elemIDs      = np.concatenate( [ nVertArray[:,None], \
                                     cell_index[:,None] ], axis=1 )
    elemIDs      = vtknp.numpy_to_vtkIdTypeArray( np.ravel( elemIDs ) )
    cellArray    = vtk.vtkCellArray()
    cellArray.SetCells( nData, elemIDs )

    # ------------------------------------------------- #
    # --- [6] uGrid making                          --- #
    # ------------------------------------------------- #
    uGrid = vtk.vtkUnstructuredGrid()
    uGrid.SetPoints(points)
    uGrid.SetCells( cell_type, offset, cellArray )

    # ------------------------------------------------- #
    # --- [7] point Data                            --- #
    # ------------------------------------------------- #
    for ik in range( nScholars ):
        pointData_   = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
        pointData_.SetName( names[ik] )
        uGrid.GetPointData().AddArray( pointData_ )

    return( uGrid )


# ========================================================= #
# ===  save as a vtk Format File                        === #
# ========================================================= #
def save__uGrid( uGrid=None, DataFormat="binary", vtkFile="out.vtu" ):
    
    writer = vtk.vtkXMLUnstructuredGridWriter()
    if   ( DataFormat.lower() == "ascii"  ):
        writer.SetDataModeToAscii()
    elif ( DataFormat.lower() == "binary" ):
        writer.SetDataModeToBinary()
    else:
        print( "[save__uGrid.py] DataFormat == ???" )
        sys.exit()
    writer.SetFileName( vtkFile )
    writer.SetInputData( uGrid )
    writer.Write()
    print( "[save__uGrid] outFile :: {0} ".format( vtkFile ) )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ 0.0, 1.0, 11 ]
    x2MinMaxNum = [ 0.0, 1.0, 11 ]
    x3MinMaxNum = [ 0.0, 1.0, 11 ]
    ret         = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "point" )
    Data        = ret
    scatter__vtkPoint( Data=Data )
