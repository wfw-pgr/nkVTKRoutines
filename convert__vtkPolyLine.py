import os, sys, vtk
import numpy                  as np
import vtk.util.numpy_support as vtknp

# --------------------------------------------------- #
# --                                               -- #
# -- For line displaying                           -- #
# --   Data = [nData,nComponents]                  -- #
# --   components = x_,y_,z_,f1_,f2_,....          -- #
# --                                               -- #
# --------------------------------------------------- #

# ========================================================= #
# ===  convert__vtkPolyLine                             === #
# ========================================================= #

def convert__vtkPolyLine( Data=None, outFile="out.vtp", DataFormat="binary", names=None ):
    polyData     = vtkPolyLine( Data=Data, names=names )
    save__vtkPolyLine( polyData=polyData, outFile=outFile, DataFormat=DataFormat )
    return()


# ========================================================= #
# ===  vtkPolyLine                                      === #
# ========================================================= #

def vtkPolyLine( Data=None, names=None ):

    x_,y_,z_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] Define structures                     --- #
    # ------------------------------------------------- #
    # -- [1-1] Data dimension check                 --  #
    if ( Data.ndim != 2 ):
        print( "[vtkPolyLine] Data's dimension is not 2...   [ERROR]" )
        print( "[vtkPolyLine] Data :: {0}".format( Data.ndim ) )
        sys.exit()
    nData       = Data.shape[0]
    nComponents = Data.shape[1]
    # -- [1-2] prepare points & lines & coordinates --  #
    pts         = vtk.vtkPoints()
    lines       = vtk.vtkCellArray()
    coordinates = Data[:,x_:z_+1]
    nScholars   = nComponents - 3
    if ( nScholars >= 1 ):
        scholars    = np.reshape( ( Data[:,z_+1:] ), (-1,nScholars) )
    # -- [1-3] names check                          --  #
    if ( names is None ):
        names = [ "line{0:02}".format( ik ) for ik in range( nScholars ) ]
    if ( len( names ) != nScholars ):
        print( "[vtkPolyLine] len( names ) does not match nScholars..... [ERROR] " )
        print( "[vtkPolyLine] Data  :: {0} ".format( Data.shape ) )
        print( "[vtkPolyLine] names :: {0} ".format( names      ) )
        sys.exit()
    # -- [1-4] length calculation -- #
    length      = np.cumsum( np.sqrt( np.sum( np.diff( coordinates, axis=0 )**2, axis=1 ) ) )
    l_norm      = np.insert( length, 0, 0.0 )
    l_norm      = vtknp.numpy_to_vtk( l_norm, deep=True )
    l_norm.SetName( "Line Length" )
    
    # ------------------------------------------------- #
    # --- [2] Define Line                           --- #
    # ------------------------------------------------- #
    index     = 0
    for ik in range( Data.shape[0]-1 ):
        # -- register points as end point           --  #
        start = Data[ik  ]
        end   = Data[ik+1]
        pts.InsertNextPoint( start[x_], start[y_], start[z_] )
        pts.InsertNextPoint(   end[x_],   end[y_],   end[z_] )
        # -- connect two point to make line         --  #
        line = vtk.vtkLine()
        line.GetPointIds().SetId( 0, index   )
        line.GetPointIds().SetId( 1, index+1 )
        index += 2
        lines.InsertNextCell( line )
    # -- set vtk poly data -- #
    polyData = vtk.vtkPolyData()
    polyData.SetPoints( pts )
    polyData.SetLines (lines)
    for ik in range( nScholars ):
        hscholar = vtknp.numpy_to_vtk( scholars[:,ik], deep=True )
        hscholar.SetName( names[ik] )
        polyData.GetCellData().AddArray( hscholar )
    polyData.GetCellData().AddArray( l_norm )
    return ( polyData )



# ========================================================= #
# ===  save as XML polyData VTK File                    === #
# ========================================================= #

def save__vtkPolyLine( polyData=None, DataFormat="binary", outFile="out.vtp" ):

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
    convert__vtkPolyLine( Data=points, outFile=outFile, names=["line01"] )

    # points       = np.zeros( (nDiv,3) )
    # points[:,x_] = np.linspace( xpt1[x_], xpt2[x_], nDiv )
    # points[:,y_] = np.linspace( xpt1[y_], xpt2[y_], nDiv )
    # points[:,z_] = np.linspace( xpt1[z_], xpt2[z_], nDiv )
    # convert__vtkPolyLine( Data=points, outFile=outFile, names=None )
    
