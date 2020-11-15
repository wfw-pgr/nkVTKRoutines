import numpy as np
import os, sys, vtk
import vtk.util.numpy_support as vtknp

# ========================================================= #
# ===  vtkDrawLine                                      === #
# ========================================================= #
def vtkDrawLine( pts=None ):

    # ------------------------------------------------- #
    # --- [1] Define structures                     --- #
    # ------------------------------------------------- #
    points     = vtk.vtkPoints()
    lines      = vtk.vtkCellArray()
    length     = np.cumsum( np.sqrt( np.sum( np.diff( pts, axis=0 )**2, axis=1 ) ) )
    l_norm     = np.insert( length, 0, 0.0 ) / float( length[-1] )
    l_norm     = vtknp.numpy_to_vtk( l_norm, deep=True )
    
    # ------------------------------------------------- #
    # --- [2] Define Line                           --- #
    # ------------------------------------------------- #
    index     = 0
    for ik in range( pts.shape[0]-1 ):
        # -- register points as end point           --  #
        start = pts[ik  ]
        end   = pts[ik+1]
        points.InsertNextPoint( start[x_], start[y_], start[z_] )
        points.InsertNextPoint(   end[x_],   end[y_],   end[z_] )
        # -- connect two point to make line         --  #
        line = vtk.vtkLine()
        line.GetPointIds().SetId( 0, index   )
        line.GetPointIds().SetId( 1, index+1 )
        index += 2
        lines.InsertNextCell( line )
    # -- set vtk poly data -- #
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.SetLines(lines)
    poly_data.GetCellData().AddArray( l_norm )
    return ( poly_data )


# ========================================================= #
# ===  save as XML polyData VTK File                    === #
# ========================================================= #

def save__vtkPolyData( polyData=None, DataFormat="ascii", vtkFile="out.vtp" ):

    # ------------------------------------------------- #
    # --- [1] save in vtp File                      --- #
    # ------------------------------------------------- #
    writer = vtk.vtkXMLPolyDataWriter()
    if ( DataFormat.lower() == "ascii"  ):
        writer.SetDataModeToAscii()
    if ( DataFormat.lower() == "binary" ):
        writer.SetDataModeToBinary()
    writer.SetFileName( vtkFile )
    writer.SetInputData( polyData )
    writer.Write()
    print( "[vtkDataConverter] output :: {0} ".format( vtkFile ) )
    return()


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    x_,y_,z_     = 0, 1, 2
    nDiv         = 101
    xpt1         = np.array( [ 0.0, 0.0, 0.0 ] )
    xpt2         = np.array( [ 1.0, 1.0, 1.0 ] )
    points       = np.zeros( (nDiv,3) )
    points[:,x_] = np.linspace( xpt1[x_], xpt2[x_], nDiv )
    points[:,y_] = np.linspace( xpt1[y_], xpt2[y_], nDiv )
    points[:,z_] = np.linspace( xpt1[z_], xpt2[z_], nDiv )
    
    polyData     = vtkDrawLine( pts=points )
    save__vtkPolyData( polyData=polyData )
