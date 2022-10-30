import numpy as np
import os, sys, vtk, re
import vtk.util.numpy_support as vtknp

# ========================================================= #
# ===  interpolate__vtk2point.py                        === #
# ========================================================= #

def interpolate__vtk2point( inpFile=None, outFile=None, coordinates=None ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ):
        sys.exit( "[interpolate__vtk2point.py] inpFile == ??? [ERROR] " )
    if ( coordinates is None ):
        sys.exit( "[interpolate__vtk2point.py] inpFile == ??? [ERROR] " )

    # ------------------------------------------------- #
    # --- [2] load vtk Data                         --- #
    # ------------------------------------------------- #
    if   ( re.match( r".*\.vtu", inpFile ) ):
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif ( re.match( r".*\.vts", inpFile ) ):
        reader = vtk.vtkXMLStructuredGridReader()
    else:
        print( "[interpolate__vtk2point.py] unsupported extention. [ERROR] " )
        print( "[interpolate__vtk2point.py] inpFile :: {0} ".format( inpFile ) )
        sys.exit()

    reader.SetFileName( inpFile )
    reader.Update()
    vtkData = reader.GetOutput()

    # ------------------------------------------------- #
    # --- [3] use probe Filter to interpolate       --- #
    # ------------------------------------------------- #
    nPoints      = coordinates.shape[0]
    nComponents  = coordinates.shape[1]
    points       = vtk.vtkPoints()
    points.SetData( vtknp.numpy_to_vtk( coordinates ) )
    polyData     = vtk.vtkPolyData()
    polyData.SetPoints( points )

    probe        = vtk.vtkProbeFilter()
    probe.SetSourceData( vtkData )
    probe.SetInputData( polyData )
    probe.Update()

    # ------------------------------------------------- #
    # --- [4] numpy data construction from probe    --- #
    # ------------------------------------------------- #
    pointData   = ( probe.GetPolyDataOutput() ).GetPointData()
    nArray      = pointData.GetNumberOfArrays()
    Data        = np.zeros( (nPoints,nArray+3) )
    Data[:,0:3] = np.copy( coordinates )
    names       = [ "xp", "yp", "zp" ]
    for ik in range( nArray ):
        names        += [ pointData.GetArrayName( ik ) ]
        Data[:,ik+3]  = vtknp.vtk_to_numpy( pointData.GetArray(ik) )

    # ------------------------------------------------- #
    # --- [5] save as a nkPointFile                 --- #
    # ------------------------------------------------- #
    if ( outFile is not None ):
        import nkUtilities.save__pointFile as spf
        spf.save__pointFile( outFile=outFile, Data=Data, names=names )
    print( "[interpolate__vtk2point.py] names :: ", names )
    
    return( Data )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    x_, y_, z_  = 0, 1, 2
    vtsFile     = "test/sample.vts"
    outFile     = "test/sample.dat"

    # ------------------------------------------------- #
    # --- [1] sample vts File generation            --- #
    # ------------------------------------------------- #
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ 0.0, 1.0, 11 ]
    x2MinMaxNum = [ 0.0, 1.0, 11 ]
    x3MinMaxNum = [ 0.0, 1.0, 11 ]
    grid        = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "structured" )
    radii       = np.sqrt( np.sum( grid**2, axis=-1 ) )
    func1       = radii**2
    func2       = radii**2 + radii + 1.0
    gridData    = np.concatenate( [grid,radii[...,None],func1[...,None],func2[...,None]], axis=-1 )
    import nkVTKRoutines.convert__vtkStructuredGrid as vsg
    vsg.convert__vtkStructuredGrid( Data=gridData, outFile=vtsFile )

    # ------------------------------------------------- #
    # --- [2] coordinate to interpolate             --- #
    # ------------------------------------------------- #
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ 0.3, 0.7, 21 ]
    x2MinMaxNum = [ 0.3, 0.7, 21 ]
    x3MinMaxNum = [ 0.3, 0.7, 21 ]
    coordinates = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "point" )

    # ------------------------------------------------- #
    # --- [3] call interpolation routine            --- #
    # ------------------------------------------------- #
    exe         = interpolate__vtk2point( inpFile=vtsFile, coordinates=coordinates, outFile=outFile )
