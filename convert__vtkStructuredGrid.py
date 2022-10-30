import os, sys, vtk
import numpy                  as np
import vtk.util.numpy_support as vtknp

# ----------------------------------------- #
# -- Data[ LK,LJ,LI,nComponents ]        -- #
# -- components :: x,y,z,f1,f2,f3,...... -- #
# ----------------------------------------- #

# ========================================================= #
# ===  convert__vtkStructuredGrid                       === #
# ========================================================= #

def convert__vtkStructuredGrid( Data=None, outFile="out.vts", names=None, shape=None, \
                                DataFormat="binary" ):
    
    # ------------------------------------------------- #
    # --- [1] Data empty check                      --- #
    # ------------------------------------------------- #
    if ( Data is None ):
        sys.exit( "[vtkStructuredGrid] Data == ???" )
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
    if   ( Data_.ndim == 4 ):
        structData   = vtkStructuredGrid3d( Data=Data_, names=names )
    elif ( Data_.ndim == 3 ):
        print( Data_.shape )
        Data_        = np.concatenate( [ Data_[:,:,0:2], \
                                         np.zeros_like( Data_[:,:,0] )[:,:,None],  \
                                         Data_[:,:,2: ] ], axis=2 )
        Data_        = Data_[None,:,:,:]
        structData   = vtkStructuredGrid3d( Data=Data_, names=names )
    else:
        print( "[convert__vtkStructuredGrid] Data dimension is not [ 2D, 3D ] " )
        print( "[convert__vtkStructuredGrid] Data shape :: [LK,LJ,LI,nComponents], [LJ,LI,nComponents] " )
        print( "[convert__vtkStructuredGrid] Data.ndim  :: {0} ".format( Data_.ndim ) )
        sys.exit()
    # ------------------------------------------------- #
    # --- [4] write structured Grid Data            --- #
    # ------------------------------------------------- #
    save__vtkStructuredGrid( structData=structData, outFile=outFile, DataFormat=DataFormat )
    return()



# ========================================================= #
# ===  vtkStructuredGrid3d                              === #
# ========================================================= #

def vtkStructuredGrid3d( Data=None, names=None ):

    x_,y_,z_ = 0, 1, 2
    # ------------------------------------------------- #
    # --- [1] Arguments Check                       --- #
    # ------------------------------------------------- #
    if ( Data is None ):
        sys.exit( "[vtkStructuredGrid] Data == ???" )
    # ------------------------------------------------- #
    # --- [2] Data size check                       --- #
    # ------------------------------------------------- #
    #  -- [2-1] Dimension check                     --  #
    if ( Data.ndim !=4 ):
        print( "[vtkStructuredGrid3d] Data dimension != 4 " )
        print( "[vtkStructuredGrid3d] Data :: {0} ".format( Data.ndim ) )
        sys.exit()
    else:
        dims         = [ Data.shape[2], Data.shape[1], Data.shape[0] ]
    #  -- [2-2] nComponents check                   --  #
    nComponents  = Data.shape[-1]
    if   ( nComponents == 3 ):
        coordinates = np.reshape( Data[:,:,:,x_:z_+1], (-1,3) )
        scholars    = np.reshape( Data[:,:,:,x_:z_+1], (-1,3) )
        if ( names is None ): names = [ "x-coordinate", "y-coordinate", "z-coordinate" ]

    elif ( nComponents >= 4 ):
        coordinates = np.reshape( Data[:,:,:,x_:z_+1], (-1,3) )
        scholars    = np.reshape( Data[:,:,:,z_+1:  ], (-1,nComponents-3) )
    #  -- [2-3] nScholars check                     --  #
    nScholars = scholars.shape[1]

    # ------------------------------------------------- #
    # --- [3] naming                                --- #
    # ------------------------------------------------- #
    if ( names is None ):
        names = [ "scholar_{0:02}".format(ik+1) for ik in range( nScholars ) ]
    if ( len( names ) != nScholars ):
        print( "[convert__vtkStructuredGrid] unmatched names & Data size .... [ERROR] " )
        print( "[convert__vtkStructuredGrid] Data size :: {0} ".format( Data.shape )    )
        print( "[convert__vtkStructuredGrid] names     :: {0} ".format( names      )    )
        
    # ------------------------------------------------- #
    # --- [4] Coordinates Points Settings           --- #
    # ------------------------------------------------- #
    #  -- [4-1] Coordinates Points                  --  #
    coordinates_ = vtknp.numpy_to_vtk( coordinates, deep=True )
    points       = vtk.vtkPoints()
    points.SetData( coordinates_ )
    #  -- [4-2] define structData / CellDataArray   --  #
    structData   = vtk.vtkStructuredGrid()
    structData.SetPoints( points )
    structData.SetDimensions( dims )
    cellArray    = vtk.vtkCellArray()
    #  -- [4-3] assign pointData to structData      --  #
    for ik in range( nScholars ):
        pointData_   = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
        pointData_.SetName( names[ik] )
        structData.GetPointData().AddArray( pointData_ )
    # ------------------------------------------------- #
    # --- [5] return structData                     --- #
    # ------------------------------------------------- #
    return( structData )


# ========================================================= #
# ===  vtkStructuredGrid2d                              === #
# ========================================================= #

def vtkStructuredGrid2d( Data=None, names=None ):

    x_,y_,z_ = 0, 1, 2
    # ------------------------------------------------- #
    # --- [1] Arguments Check                       --- #
    # ------------------------------------------------- #
    if ( Data is None ):
        sys.exit( "[vtkStructuredGrid2d] Data == ???" )
    # ------------------------------------------------- #
    # --- [2] Data size check                       --- #
    # ------------------------------------------------- #
    #  -- [2-1] Dimension check                     --  #
    if ( Data.ndim != 3 ):
        print( "[vtkStructuredGrid2d] Data dimension != 3 " )
        print( "[vtkStructuredGrid2d] Data :: {0} ".format( Data.ndim ) )
        sys.exit()
    else:
        dims         = [ 1, Data.shape[1], Data.shape[0] ]
    #  -- [2-2] nComponents check                   --  #
    nComponents  = Data.shape[-1]
    if   ( nComponents == 2 ):
        coordinates = np.reshape( Data[:,:,x_:y_+1], (-1,2) )
        scholars    = np.reshape( Data[:,:,x_:y_+1], (-1,2) )
        if ( names is None ): names = [ "x-coordinate", "y-coordinate" ]
        names       
    elif ( nComponents >= 3 ):
        coordinates = np.reshape( Data[:,:,x_:y_+1], (-1,2) )
        scholars    = np.reshape( Data[:,:,y_+1:  ], (-1,nComponents-2) )
    #  -- [2-3] nScholars check                     --  #
    nScholars = scholars.shape[1]

    # ------------------------------------------------- #
    # --- [3] naming                                --- #
    # ------------------------------------------------- #
    if ( names is None ):
        names = [ "scholar_{0:02}".format(ik+1) for ik in range( nScholars ) ]
    if ( len( names ) != nScholars ):
        print( "[convert__vtkStructuredGrid] unmatched names & Data size .... [ERROR] " )
        print( "[convert__vtkStructuredGrid] Data size :: {0} ".format( Data.shape )    )
        print( "[convert__vtkStructuredGrid] names     :: {0} ".format( names      )    )
        
    # ------------------------------------------------- #
    # --- [4] Coordinates Points Settings           --- #
    # ------------------------------------------------- #
    #  -- [4-1] Coordinates Points                  --  #
    coordinates_ = vtknp.numpy_to_vtk( coordinates, deep=True )
    points       = vtk.vtkPoints()
    points.SetData( coordinates_ )
    #  -- [4-2] define structData / CellDataArray   --  #
    structData   = vtk.vtkStructuredGrid()
    structData.SetPoints( points )
    print( dims )
    structData.SetDimensions( dims )
    cellArray    = vtk.vtkCellArray()
    #  -- [4-3] assign pointData to structData      --  #
    for ik in range( nScholars ):
        pointData_   = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
        pointData_.SetName( names[ik] )
        structData.GetPointData().AddArray( pointData_ )
    # ------------------------------------------------- #
    # --- [5] return structData                     --- #
    # ------------------------------------------------- #
    return( structData )

    
# ========================================================= #
# ===  save as XML polyData VTK File                    === #
# ========================================================= #

def save__vtkStructuredGrid( structData=None, DataFormat="binary", outFile="out.vtp" ):

    # ------------------------------------------------- #
    # --- [1] save in vtp File                      --- #
    # ------------------------------------------------- #
    writer = vtk.vtkXMLStructuredGridWriter()
    if ( DataFormat.lower() == "ascii"  ):
        writer.SetDataModeToAscii()
    if ( DataFormat.lower() == "binary" ):
        writer.SetDataModeToBinary()
    writer.SetFileName( outFile )
    writer.SetInputData( structData )
    writer.Write()
    print( "[save__vtkStructuredGrid] output :: {0} ".format( outFile ) )
    return()



# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] test for 3D                           --- #
    # ------------------------------------------------- #    
    x_,y_,z_,f_       = 0, 1, 2, 3
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum       = [ -1.0, 1.0, 41 ]
    x2MinMaxNum       = [ -1.0, 1.0, 31 ]
    x3MinMaxNum       = [ -0.0, 0.0,  1 ]
    ret               = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                           x3MinMaxNum=x3MinMaxNum, returnType = "structured" )
    LK, LJ, LI        = ret.shape[0], ret.shape[1], ret.shape[2]
    Data              = np.zeros( (LK,LJ,LI,4) )
    Data[...,x_:z_+1] = ret[...,x_:z_+1]
    Data[...,f_]      = np.sqrt( ret[...,x_]**2 + ret[...,y_]**2 )
    print( Data.shape )

    convert__vtkStructuredGrid( Data=Data, outFile="test/cvs_test01.vts" )

    # ------------------------------------------------- #
    # --- [2] test for 2D                           --- #
    # ------------------------------------------------- #    
    x_,y_,f_          = 0, 1, 2
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum       = [ -1.0, 1.0, 41 ]
    x2MinMaxNum       = [ -1.0, 1.0, 31 ]
    x3MinMaxNum       = [ -0.0, 0.0,  1 ]
    ret               = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                           x3MinMaxNum=x3MinMaxNum, returnType = "structured" )
    ret[...,f_]       = np.sqrt( ret[...,x_]**2 + ret[...,y_]**2 )
    Data              = np.copy( ret[0,:,:,:] )
    print( Data.shape )
    
    convert__vtkStructuredGrid( Data=Data, outFile="test/cvs_test02.vts" )


    

# # ========================================================= #
# # ===  vtkStructuredGrid2d                              === #
# # ========================================================= #

# def vtkStructuredGrid2d( Data=None, names=None ):

#     x_,y_,z_ = 0, 1, 2
#     # ------------------------------------------------- #
#     # --- [1] Arguments Check                       --- #
#     # ------------------------------------------------- #
#     #  -- [1-1] Argument None Check                 --  #
#     if ( Data is None ): sys.exit( "[vtkStructuredGrid] Data == ???" )
#     #  -- [1-2] Data Dimension Check                --  #
#     if ( Data.ndim !=3 ):
#         print( "[vtkStructuredGrid2d] Data dimension != 3 " )
#         print( "[vtkStructuredGrid2d] Data :: {0} ".format( Data.ndim ) )
#         sys.exit()
#     else:
#         dims         = [ Data.shape[1], Data.shape[0] ]
#     #  -- [1-3] Data nComponents Check              --  #
#     nComponents  = Data.shape[-1]
#     if   ( nComponents == 2 ):
#         coordinates = np.reshape( Data[:,:,x_:y_+1], (-1,2) )
#         scholars    = np.reshape( Data[:,:,x_:y_+1], (-1,2) )
#     elif ( nComponents >= 3 ):
#         coordinates = np.reshape( Data[:,:,x_:y_+1], (-1,2) )
#         scholars    = np.reshape( Data[:,:,y_+1:  ], (-1,nComponents-2) )
#     nScholars = scholars.shape[1]
    
#     if ( names is None ):
#         names = [ "Data{0:02}".format(ik) for ik in range( nScholars ) ]
#     if ( len( names ) != nScholars ):
#         print( "[convert__vtkStructuredGrid] unmatched names & Data size .... [ERROR] " )
#         print( "[convert__vtkStructuredGrid] Data size :: {0} ".format( Data.shape )    )
#         print( "[convert__vtkStructuredGrid] names     :: {0} ".format( names      )    )
        
#     # ------------------------------------------------- #
#     # --- [2] Coordinates Points Settings           --- #
#     # ------------------------------------------------- #
#     #  -- [2-1] Coordinates Points                  --  #
#     coordinates_ = vtknp.numpy_to_vtk( coordinates, deep=True )
#     points       = vtk.vtkPoints()
#     points.SetData( coordinates_ )
#     #  -- [2-2] define structData / CellDataArray   --  #
#     structData   = vtk.vtkStructuredGrid()
#     structData.SetPoints( points )
#     structData.SetDimensions( dims )
#     cellArray    = vtk.vtkCellArray()
#     #  -- [2-3] assign pointData to structData      --  #
#     for ik in range( nScholars ):
#         pointData_   = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
#         pointData_.SetName( names[ik] )
#         structData.GetPointData().AddArray( pointData_ )
#     # ------------------------------------------------- #
#     # --- [3] return structData                     --- #
#     # ------------------------------------------------- #
#     return( structData )

