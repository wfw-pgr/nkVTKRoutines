import numpy as np
import vtk
import vtk.util.numpy_support as npv


# ========================================================= #
# ===  construct vtk unstructuredgrid                   === #
# ========================================================= #

class construct__ugrid:

    
    # ========================================================= #
    # ===  initial settings                                 === #
    # ========================================================= #
    def __init__( self, nodes=None, elems   =None, vtkFile  ="out.vtu", DataFormat="ascii", \
                  elementType=None, cellData=None, pointData=None, cellDataName=None, pointDataName=None ):

        # ------------------------------------------------- #
        # --- [1] ID_TYPE Definition ( type for IDs )   --- #
        # ------------------------------------------------- #
        if vtk.VTK_ID_TYPE == 12:
            self.ID_TYPE = np.int64
        else:
            self.ID_TYPE = np.int32

        # ------------------------------------------------- #
        # --- [2] input variables and its size          --- #
        # ------------------------------------------------- #
        self.vtkFile       = vtkFile
        self.DataFormat    = DataFormat
        self.elementType   = elementType
        self.nodes         = np.copy( nodes     )
        self.elems         = np.copy( elems     )
        self.nElem         = self.elems.shape[0]
        self.nVert         = self.elems.shape[1]
        if ( self.elems.dtype != self.ID_TYPE ):
            self.elems.astype( self.ID_TYPE )
        if ( self.elems.flags['C_CONTIGUOUS'] != True ):
            self.elems     = np.ascontiguousarray( self.elems )

        # ------------------------------------------------- #
        # --- [3] cell & point Data                     --- #
        # ------------------------------------------------- #

        if ( cellData  is not None ):
            if ( cellData.ndim == 1 ):
                cellData = np.reshape( cellData, (-1,1) )
            elif ( cellData.ndim > 2 ):
                sys.exit( "[construct__uGrid] cellData shape == {0} ".format( cellData.shape ) )
            self.cellData     = np.copy( cellData  )
            if ( cellDataName is None ):
                self.cellDataName = [ "eData{0:02}".format(ik+1) for ik in range( cellData.shape[1] ) ]
        else:
            self.cellData     = None
            self.cellDataName = None

        if ( pointData is not None ):
            if ( pointData.ndim == 1 ):
                pointData = np.reshape( pointData, (-1,1) )
            elif ( pointData.ndim > 2 ):
                sys.exit( "[construct__uGrid] pointData shape == {0} ".format( pointData.shape ) )
            self.pointData    = np.copy( pointData )
            if ( pointDataName is None ):
                self.pointDataName = [ "pData{0:02}".format(ik+1) for ik in range( pointData.shape[1] ) ]
        else:
            self.pointData     = None
            self.pointDataName = None

        
        # ------------------------------------------------- #
        # --- [3] make unstructuredGridData             --- #
        # ------------------------------------------------- #
        self.make__uGrid()
        self.save__uGrid()


    # ========================================================= #
    # ===  store elems & nodes in a ugrid format            === #
    # ========================================================= #
    def make__uGrid( self ):
            
        # ------------------------------------------------- #
        # --- [1] element IDs & offset = define cells   --- #
        # ------------------------------------------------- #
        #  -- [1-1] offset & elemIDs                    --  #
        nVertArray   = np.sum( np.ones_like( self.elems ), axis=1 )
        offset       = np.cumsum( np.insert( nVertArray, 0, 0.0 ) )
        offset       = npv.numpy_to_vtkIdTypeArray( ( offset[:-1] ).astype( self.ID_TYPE ) )
        
        #  -- [1-2] cell type                           --  #
        if ( self.elementType is not None ):
            cellType = np.full( ( self.nElem,), self.elementType    )
        if ( self.nVert == 4 ):
            cellType = np.full( ( self.nElem,), vtk.VTK_TETRAHEDRON )
        if ( self.nVert == 8 ):
            cellType = np.full( ( self.nElem,), vtk.VTK_HEXAHEDRON  )
        cellType     = cellType.astype( np.uint8 )
        cellType     = npv.numpy_to_vtk( cellType )

        #  -- [1-3] cell array                          --  #
        elemIDs      = np.concatenate( [ np.reshape( nVertArray, ( self.nElem,1) ), \
                                         self.elems ], axis=1 )
        elemIDs      = npv.numpy_to_vtkIdTypeArray( np.ravel( elemIDs ) )
        cellArray    = vtk.vtkCellArray()
        cellArray.SetCells( self.nElem, elemIDs )
        # -- elemID Data Structure -- #
        # [ [ N, e1, e2, e3, ...., eN ], [ N, e1, e2, e3, ...., eN ], .... ]
        # -- 
        
        # ------------------------------------------------- #
        # --- [2] node definition                       --- #
        # ------------------------------------------------- #
        vtkPoints    = vtk.vtkPoints()
        vtkPoints.SetData( npv.numpy_to_vtk( self.nodes ) )

        # ------------------------------------------------- #
        # --- [3] Define unstructured Grid              --- #
        # ------------------------------------------------- #
        self.ugrid = vtk.vtkUnstructuredGrid()
        self.ugrid.SetPoints( vtkPoints )
        self.ugrid.SetCells( cellType, offset, cellArray )

        # ------------------------------------------------- #
        # --- [4] cellData & pointData                  --- #
        # ------------------------------------------------- #
        #  -- [4-1] cellData                            --  #
        if ( self.cellData is not None ):
            self.cellDataDict = { key: npv.numpy_to_vtk( self.cellData[:,ik], deep=True ) \
                                  for ik,key in enumerate( self.cellDataName ) }
            for key in self.cellDataName:
                self.cellDataDict[key].SetName( key )
                self.ugrid.GetCellData().AddArray( self.cellDataDict[key] )

        #  -- [4-2] pointData                           --  #
        if ( self.pointData is not None ):
            self.pointDataDict = { key: npv.numpy_to_vtk( self.pointData[:,ik], deep=True ) \
                                  for ik,key in enumerate( self.pointDataName ) }
            for key in self.pointDataName:
                self.pointDataDict[key].SetName( key )
                self.ugrid.GetPointData().AddArray( self.pointDataDict[key] )
        

        
    # ========================================================= #
    # ===  save as a vtk Format File                        === #
    # ========================================================= #
    def save__uGrid( self, DataFormat=None, vtkFile=None ):

        if ( DataFormat is not None ):
            self.DataFormat = DataFormat
        if ( vtkFile    is not None ):
            self.vtkFile    = vtkFile
    
        self.writer = vtk.vtkXMLUnstructuredGridWriter()
        self.writer.SetDataModeToBinary()
        if ( self.DataFormat.lower() == "ascii"  ):
            self.writer.SetDataModeToAscii()
        if ( self.DataFormat.lower() == "binary" ):
            self.writer.SetDataModeToBinary()
        self.writer.SetFileName( self.vtkFile )
        self.writer.SetInputData( self.ugrid )
        self.writer.Write()
        print( "[save__uGrid] outFile :: {0} ".format( self.vtkFile ) )




# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ 0.0, 1.0, 2 ]
    x2MinMaxNum = [ 0.0, 2.0, 2 ]
    x3MinMaxNum = [ 0.0, 3.0, 3 ]
    nodes       = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "point", \
                                     DataOrder  ="ijk" )
    
    elems       = np.array( [ [ 0, 1, 3, 2, 4, 5,  7,  6 ], \
                              [ 4, 5, 7, 6, 8, 9, 11, 10 ]  ] )
    cellData    = np.array( [ [ 1.0, 2.0, 3.0 ], [0.0, 1.0, 2.0] ] )
    pointData1  = np.sqrt( nodes[:,0]**2 + nodes[:,1]**2, nodes[:,2]**2 )
    pointData2  = np.exp( - 0.5 * nodes[:,0]**2 + nodes[:,1]**2, nodes[:,2]**2 )
    pointData   = np.concatenate( ( pointData1[:,None], pointData2[:,None] ), axis=1 )
    
    construct__ugrid( nodes=nodes, elems=elems, cellData=cellData, pointData=pointData, vtkFile="out.vtu" )
