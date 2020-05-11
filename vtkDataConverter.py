import os, sys, subprocess
import vtk
import numpy                        as np
import nkVTKRoutines.vtkDataManager as vdm
import vtk.util.numpy_support       as vtknp


# ========================================================= #
# ===  vtkDataWriter                                    === #
# ========================================================= #

class vtkDataConverter( vdm.vtkDataManager ):

    # ------------------------------------------------- #
    # --- constructor                               --- #
    # ------------------------------------------------- #

    def __init__( self, Data=None, tag=None, DataOrder=None, DataType=None, shape=None, \
                  vtkFile="out.vtu", vtkFileType=None, DataFormat="ascii", newFile=True ):

        # ------------------------------------------------- #
        # --- call fieldDataManager initialization      --- #
        # ------------------------------------------------- #
        super().__init__( Data=Data, tag=tag, DataOrder=DataOrder, \
                          DataType=DataType, shape=shape )
        
        # ------------------------------------------------- #
        # --- vtk native variables                      --- #
        # ------------------------------------------------- #
        self.vtkFile     = vtkFile
        self.DataFormat  = DataFormat

        # ------------------------------------------------- #
        # --- inspect vtkFileType                       --- #
        # ------------------------------------------------- #
        extention = ( vtkFile.split( "." ) )[-1]
        if   ( extention == "vti" ):
            self.vtkFileType = "ImageData"
            self.image       = vtk.vtkImageData()
        elif ( extention == "vts" ):
            self.vtkFileType = "StructuredGrid"
            self.sGrid       = vtk.vtkStructuredGrid()
        elif ( extention == "vtu" ):
            self.vtkFileType = "UnstructuredGrid"
            self.uGrid       = vtk.vtkUnstructuredGrid()
        elif ( extention == "vtp" ):
            self.vtkFileType = "PolyData"
            self.pData       = vtk.vtkPolyData()
        else:
            print( "[vtkDataWriter] Unknown extention :: {0}".format( extention ) )
            print( "[vtkDataWriter]         vtkFile   :: {0}".format( vtkFile   ) )
            print( "[vtkDataWriter] please specify extention from .vti, .vts, .vtu " )
            sys.exit()

        # ------------------------------------------------- #
        # --- single Data convert                       --- #
        # ------------------------------------------------- #
        if ( ( Data is not None ) and ( tag is not None ) ):
            if ( self.vtkFileType == "ImageData" ):
                self.convert__imageData2vti( tag=tag )
            if ( self.vtkFileType == "StructuredGrid" ):
                self.convert__pointData2vts( tag=tag )
            if ( self.vtkFileType == "UnstructuredGrid" ):
                self.convert__pointData2vtu( tag=tag )
            if ( self.vtkFileType == "PolyData" ):
                self.generate__surfacePolyData( tag=tag )

                
    # ------------------------------------------------- #
    # --- add Unstructured Data from pointData      --- #
    # ------------------------------------------------- #
    
    def convert__pointData2vtu( self, tag=None ):

        # ------------------------------------------------- #
        # --- [1] Arguments Check                       --- #
        # ------------------------------------------------- #
        if ( tag is None ): sys.exit( "[convert__pointData2vtu -@vtkDataManager-] tag == ???" )
        if ( self.Data[tag].fieldData is None ):
            self.Data[tag].generate__fieldData()
        if ( self.Data[tag].coordinateData is None ):
            self.Data[tag].generate__coordinateData()
        # ------------------------------------------------- #
        # --- [2] Coordinates Points Settings           --- #
        # ------------------------------------------------- #
        coordinates_ = vtknp.numpy_to_vtk( self.Data[tag].coordinateData, deep=True )
        points       = vtk.vtkPoints()
        points.SetData( coordinates_ )
        self.uGrid.SetPoints( points )
        # ------------------------------------------------- #
        # --- [3] store points & pointData              --- #
        # ------------------------------------------------- #
        for ik in range( self.Data[tag].nFields ):
            pointData_   = vtknp.numpy_to_vtk( self.Data[tag].fieldData[:,ik], deep=True )
            pointData_.SetName( self.Data[tag].fieldLabel[ik] )
            self.uGrid.GetPointData().AddArray( pointData_ )
        # ------------------------------------------------- #
        # --- [4] Delaunay triangulation                --- #
        # ------------------------------------------------- #
        delaunay = vtk.vtkDelaunay3D()
        delaunay.SetInputData( self.uGrid )
        delaunay.Update()
        # ------------------------------------------------- #
        # --- [5] save in vtu File                      --- #
        # ------------------------------------------------- #
        writer = vtk.vtkXMLUnstructuredGridWriter()
        if ( self.DataFormat.lower() == "ascii"  ):
            writer.SetDataModeToAscii()
        if ( self.DataFormat.lower() == "binary" ):
            writer.SetDataModeToBinary()
        writer.SetFileName( self.vtkFile )
        writer.SetInputData( delaunay.GetOutput() )
        writer.Write()
        print( "[vtkDataConverter] output :: {0} ".format( self.vtkFile ) )


    # ------------------------------------------------- #
    # --- add Structured Data from pointData        --- #
    # ------------------------------------------------- #

    def convert__pointData2vts( self, tag=None ):

        # ------------------------------------------------- #
        # --- [1] Arguments Check                       --- #
        # ------------------------------------------------- #
        if ( tag is None ): sys.exit( "[convert__pointData2vts -@vtkDataManager-] tag == ???" )
        if ( self.Data[tag].fieldData      is None ):
            self.Data[tag].generate__fieldData()
        if ( self.Data[tag].coordinateData is None ):
            self.Data[tag].generate__coordinateData()
        # ------------------------------------------------- #
        # --- [2] Coordinates Points Settings           --- #
        # ------------------------------------------------- #
        coordinates_ = vtknp.numpy_to_vtk( self.Data[tag].coordinateData, deep=True )
        points       = vtk.vtkPoints()
        points.SetData( coordinates_ )
        self.sGrid.SetPoints( points )
        # ------------------------------------------------- #
        # --- [3] store points & pointData              --- #
        # ------------------------------------------------- #
        for ik in range( self.Data[tag].nFields ):
            pointData_   = vtknp.numpy_to_vtk( self.Data[tag].fieldData[:,ik], deep=True )
            pointData_.SetName( self.Data[tag].fieldLabel[ik] )
            self.sGrid.GetPointData().AddArray( pointData_ )
        self.sGrid.SetExtent ( self.Data[tag].Extent )
        # ------------------------------------------------- #
        # --- [4] save in vtu File                      --- #
        # ------------------------------------------------- #
        writer = vtk.vtkXMLStructuredGridWriter()
        if ( self.DataFormat.lower() == "ascii"  ):
            writer.SetDataModeToAscii()
        if ( self.DataFormat.lower() == "binary" ):
            writer.SetDataModeToBinary()
        writer.SetFileName( self.vtkFile )
        writer.SetInputData( self.sGrid )
        writer.Write()
        print( "[vtkDataConverter] output :: {0} ".format( self.vtkFile ) )


    # ------------------------------------------------- #
    # --- add Structured Data from pointData        --- #
    # ------------------------------------------------- #

    def convert__imageData2vti( self, tag=None ):

        # ------------------------------------------------- #
        # --- [1] Arguments Check                       --- #
        # ------------------------------------------------- #
        if ( tag is None ): sys.exit( "[convert__pointData2vts -@vtkDataManager-] tag == ???" )
        if ( self.Data[tag].pointData      is None ):
            self.Data[tag].generate__pointData()
        # ------------------------------------------------- #
        # --- [2] Preparation                           --- #
        # ------------------------------------------------- #
        imageData_ = vtknp.numpy_to_vtk( self.Data[tag].pointData, deep=True )
        imageData_.SetName( tag )
        # ------------------------------------------------- #
        # --- [3] store points & pointData              --- #
        # ------------------------------------------------- #
        self.image.GetPointData().AddArray( imageData_ )
        self.image.SetExtent ( self.Data[tag].Extent  )
        # ------------------------------------------------- #
        # --- [4] save in vtu File                      --- #
        # ------------------------------------------------- #
        writer = vtk.vtkXMLImageDataWriter()
        if ( self.DataFormat.lower() == "ascii"  ):
            writer.SetDataModeToAscii()
        if ( self.DataFormat.lower() == "binary" ):
            writer.SetDataModeToBinary()
        writer.SetFileName( self.vtkFile )
        writer.SetInputData( self.image )
        writer.Write()
        print( "[vtkDataConverter] output :: {0} ".format( self.vtkFile ) )


    # ------------------------------------------------- #
    # --- generate polyData for 3D-surface plot     --- #
    # ------------------------------------------------- #
    
    def generate__surfacePolyData( self, tag=None ):

        # ------------------------------------------------- #
        # --- [1] Arguments Check                       --- #
        # ------------------------------------------------- #
        if ( tag is None ): sys.exit( "[convert__pointData2vtu -@vtkDataManager-] tag == ???" )
        if ( self.Data[tag].fieldData is None ):
            self.Data[tag].generate__fieldData()
        if ( self.Data[tag].coordinateData is None ):
            self.Data[tag].generate__coordinateData()
        # ------------------------------------------------- #
        # --- [2] Coordinates Points Settings           --- #
        # ------------------------------------------------- #
        #  -- [2-1] Coordinates Points                  --  #
        coordinates_ = vtknp.numpy_to_vtk( self.Data[tag].coordinateData, deep=True )
        points       = vtk.vtkPoints()
        points.SetData( coordinates_ )
        #  -- [2-2] define PolyData / CellDataArray     --  #
        self.pData   = vtk.vtkPolyData()
        self.pData.SetPoints( points )
        cellArray    = vtk.vtkCellArray()
        #  -- [2-3] assign pointData to polyData        --  #
        for ik in range( self.Data[tag].nFields ):
            pointData_   = vtknp.numpy_to_vtk( self.Data[tag].fieldData[:,ik], deep=True )
            pointData_.SetName( self.Data[tag].fieldLabel[ik] )
            self.pData.GetPointData().AddArray( pointData_ )
        #  -- [2-4] boundary for Delaunay2D             --  #
        boundary     = vtk.vtkPolyData()
        boundary.SetPoints( self.pData.GetPoints() )
        boundary.SetPolys ( cellArray )
        # ------------------------------------------------- #
        # --- [3] Delaunay triangulation                --- #
        # ------------------------------------------------- #
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData ( self.pData )
        delaunay.SetSourceData( boundary  )
        delaunay.Update()
        # ------------------------------------------------- #
        # --- [4] save in vtu File                      --- #
        # ------------------------------------------------- #
        writer = vtk.vtkXMLPolyDataWriter()
        if ( self.DataFormat.lower() == "ascii"  ):
            writer.SetDataModeToAscii()
        if ( self.DataFormat.lower() == "binary" ):
            writer.SetDataModeToBinary()
        writer.SetFileName( self.vtkFile )
        writer.SetInputData( delaunay.GetOutput() )
        writer.Write()
        print( "[vtkDataConverter] output :: {0} ".format( self.vtkFile ) )


        
# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] test profiles                         --- #
    # ------------------------------------------------- #
    import nkUtilities.generate__testprofile as gtp
    x1MinMaxNum = [ 0.0, 1.0, 21 ]
    x2MinMaxNum = [ 0.0, 1.0, 21 ]
    x3MinMaxNum = [ 0.0, 1.0, 21 ]
    Data        = gtp.generate__testprofile( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
    	                                     x3MinMaxNum=x3MinMaxNum, returnType = "structured" )

    # ------------------------------------------------- #
    # --- [2] unstructured grid                     --- #
    # ------------------------------------------------- #
    
    cvt         = vtkDataConverter( vtkFile="out.vtu" )
    cvt.add__vtkDataUnit ( Data=Data, tag="sample", DataType="structured" )
    uData       = cvt.Data["sample"].generate__pointData()
    
    ref_radius  = 1.0
    radii       = np.sqrt( uData[:,0]**2 + uData[:,1]**2 + uData[:,2]**2 )
    index       = np.where( radii < ref_radius )
    uData       = uData[index][:]
    iData       = np.zeros( ( uData.shape[0], uData.shape[1]+1 ) )
    iData[:,:4] = np.copy( uData )
    iData[:, 4] = radii[index]
    
    cvt         = vtkDataConverter( vtkFile="out.vtu", Data=iData, \
                                    tag="sample", DataType="point" )

    # ------------------------------------------------- #
    # --- [3] structured grid                       --- #
    # ------------------------------------------------- #
    
    cvt         = vtkDataConverter( vtkFile="out.vts", Data=Data, \
                                    tag="sample", DataType="structured" )
    
    # ------------------------------------------------- #
    # --- [4] structured grid                       --- #
    # ------------------------------------------------- #

    image       = Data[:,:,:,3]
    cvt         = vtkDataConverter( vtkFile="out.vti", Data=image, \
                                    tag="sample", DataType="image" )

    
    # ------------------------------------------------- #
    # --- [5] poly Data surface                     --- #
    # ------------------------------------------------- #
    
    import nkUtilities.generate__testprofile as gtp
    x1MinMaxNum = [ -1.0, 1.0, 51 ]
    x2MinMaxNum = [ -1.0, 1.0, 51 ]
    x3MinMaxNum = [  0.0, 0.0,  1 ]
    Data        = gtp.generate__testprofile( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
    	                                     x3MinMaxNum=x3MinMaxNum, returnType = "point" )

    ref_radius  = 1.0
    radii       = np.sqrt( Data[:,0]**2 + Data[:,1]**2 )
    index       = np.where( radii < ref_radius )
    Data        = Data[index][:]
    radii       = radii[index]
    freq        = 2.0*np.pi*3.0/np.sqrt(2)
    Data[:,2]   = np.sin( freq * radii ) / ( freq*radii + 0.0001 )
    Data[:,3]   = np.sin( freq * radii ) / ( freq*radii + 0.0001 )
    
    cvt         = vtkDataConverter( vtkFile="out.vtp", Data=Data, \
                                    tag="sample", DataType="point" )
