import sys
import numpy as np


# ========================================================= #
# ===  vtk Data Structure unit                          === #
# ========================================================= #
class vtkDataUnit():

    # ------------------------------------------------- #
    # --- vtk Data initialize                       --- #
    # ------------------------------------------------- #
    def __init__( self      , Data  =None, tag    =None, DataOrder =None , DataType =None, \
                  shape=None, Origin=None, Spacing=None, vectorData=False, DataLabel=None ):
        # ------------------------------------------------- #
        # --- [1] prepare variables                     --- #
        # ------------------------------------------------- #
        self.Data            = None
        self.tag             = None
        self.DataOrder       = None
        self.DataType        = None
        self.DataLabel       = None
        self.ndim            = None
        self.nComponents     = None
        self.nData           = None
        self.shape           = None
        self.Extent          = None
        self.pointData       = None
        self.imageData       = None
        self.structuredData  = None
        self.coordinates     = None
        self.coordinateData  = None
        self.coordinateLabel = None
        self.fields          = None
        self.fieldData       = None
        self.fieldLabel      = None
        # ------------------------------------------------- #
        # --- [2] store input variables if exist        --- #
        # ------------------------------------------------- #
        if ( Data is not None ):
            self.store__inputData( Data =Data, tag=tag, DataOrder=DataOrder, DataType=DataType, \
                                   shape=shape, vectorData=vectorData, DataLabel=DataLabel )  

    # ------------------------------------------------- #
    # --- store inputed original Data               --- #
    # ------------------------------------------------- #
    def store__inputData( self,  Data=None, tag =None, DataOrder=None, DataType=None, \
                          shape=None, vectorData=False, DataLabel=None ):
        # ------------------------------------------------- #
        # --- [1] compulsory data components            --- #
        # ------------------------------------------------- #
        if ( Data is None ): sys.exit( "[sotre__inputData -@vtkDataUnit-] Data == ???" )
        if ( tag  is None ): sys.exit( "[sotre__inputData -@vtkDataUnit-] tag  == ???" )
        self.Data = Data
        self.tag  = tag

        # ------------------------------------------------- #
        # --- [2] store attributes                      --- #
        # ------------------------------------------------- #
        self.DataOrder    = DataOrder
        self.DataType     = DataType
        self.shape        = shape
        self.vectorData   = vectorData
        self.variableType = None
        self.ndim         = self.Data.ndim
        self.DataLabel    = DataLabel
        
        #  -- [2-1] DataOrder :: normally :: ijk        --  #
        if ( self.DataOrder is None ):
            self.DataOrder = "ijk"
            
        #  -- [2-2] DataType  :: default depend on ndim --  #
        if ( self.DataType  is None ):
            if   ( self.Data.ndim == 1 ):
                self.DataType = "1darray"
            elif ( self.Data.ndim == 2 ):
                self.DataType = "point"
            elif ( self.Data.ndim  > 3 ):
                self.DataType = "structured"

        #  -- [2-3] shape                               --  #
        if ( self.shape is None ):
            if ( self.DataType == "structured" ):
                self.shape = self.Data.shape
            if ( self.DataType == "image" ):
                if ( self.DataOrder == "ijk" ):
                    self.shape = tuple( list( self.Data.shape ) + [1] )
                if ( self.DataOrder == "kji" ):
                    self.shape = tuple( [1] + list( self.Data.shape ) )
        if ( self.shape is not None ):
            self.Extent = [ 0, 0, 0, 0, 0, 0 ]
            if ( self.DataOrder == "ijk" ):
                for ik in range( len( self.shape )-1 ):
                    self.Extent[2*ik+1] = self.shape[ik] - 1
            if ( self.DataOrder == "kji" ):
                for ik in range( len( self.shape )-1 ):
                    self.Extent[2*ik+1] = self.shape[ik]
                    
        # ------------------------------------------------- #
        # --- [3] resolve nComponents / nData           --- #
        # ------------------------------------------------- #
        if   ( self.DataType in [ "1darray", "image" ] ):
            self.nData       = self.Data.size
            self.nComponents = 1
            
        elif ( self.DataType == "point"      ):
            self.nData       = self.Data.shape[0]
            self.nComponents = self.Data.shape[1]
            
        elif ( self.DataType == "structured" ):
            if   ( self.DataOrder == "ijk" ):
                self.nData       = np.prod( self.Data.shape[:-1] )
                self.nComponents = self.Data.shape[-1]
            elif ( self.DataOrder == "kji" ):
                self.nData       = np.prod( self.Data.shape[1: ] )
                self.nComponents = self.Data.shape[ 0]

        # ------------------------------------------------- #
        # --- [4] resolve vtk Data Format               --- #
        # ------------------------------------------------- #
        if ( self.Data.dtype == np.int32   ): self.variableType = "Int32"
        if ( self.Data.dtype == np.int64   ): self.variableType = "Int64"
        if ( self.Data.dtype == np.float32 ): self.variableType = "Float32"
        if ( self.Data.dtype == np.float64 ): self.variableType = "Float64"
        
        # ------------------------------------------------- #
        # --- [5] resolve DataLabel                     --- #
        # ------------------------------------------------- #
        if ( self.DataLabel is None ):
            self.DataLabel = [ "{0}{1}".format( tag, ik ) for ik in range( self.nComponents ) ]
        
        
    # ------------------------------------------------- #
    # --- return input Data information             --- #
    # ------------------------------------------------- #
    def inspect__inputData( self ):
        ret = { "tag"  :self.tag  , "DataOrder"  :self.DataOrder  , "DataType":self.DataType,\
                "nData":self.nData, "nComponents":self.nComponents, "shape"   :self.shape,   }
        return( ret )

                
    # ------------------------------------------------- #
    # --- generate point Type Data                  --- #
    # ------------------------------------------------- #
    def generate__pointData( self ): 
        # ------------------------------------------------- #
        # --- [1] if DataType == point ; copy it        --- #
        # ------------------------------------------------- #
        if   ( self.DataType == "point"      ):
            self.pointData = self.Data
            return( self.pointData )
        # ------------------------------------------------- #
        # --- [2] otherwise 1 ; reshape & store Data    --- #
        # ------------------------------------------------- #
        if ( self.DataType in [ "1darray", "image" ] ):
            pdShape        = ( self.nData, self.nComponents )
            self.pointData = np.reshape( self.Data, pdShape )
            return( self.pointData )
        # ------------------------------------------------- #
        # --- [3] otherwise 2 ; reshape & store Data    --- #
        # ------------------------------------------------- #
        if ( self.DataType == "structured" ):
            pdShape = ( self.nData, self.nComponents )
            if   ( self.DataOrder == "ijk" ):
                self.pointData = np.reshape(               self.Data  , pdShape )
            elif ( self.DataOrder == "kji" ):
                self.pointData = np.reshape( np.transpose( self.Data ), pdShape )
            return( self.pointData )

        
    # ------------------------------------------------- #
    # --- generate structured Type Data             --- #
    # ------------------------------------------------- #
    def generate__structuredData( self ):
        # ------------------------------------------------- #
        # --- [0] shape exist check                     --- #
        # ------------------------------------------------- #
        if ( self.shape is None ):
            sys.exit( "[generate__structuredData -@vtkDataUnit-] self.shape is None [ERROR]" )
        # ------------------------------------------------- #
        # --- [1] structured case ; copy it             --- #
        # ------------------------------------------------- #
        if ( self.DataType == "structured" ):
            self.structuredData = self.Data
        # ------------------------------------------------- #
        # --- [2] 1darray / image case ; reshape        --- #
        # ------------------------------------------------- #
        if ( self.DataType in [ "1darray", "image" ] ):
            self.structuredData = np.reshape( self.Data, self.shape )
        # ------------------------------------------------- #
        # --- [3] point case ; reshape                  --- #
        # ------------------------------------------------- #
        if ( self.DataType == "point" ):
            self.structuredData = np.reshape( self.Data, self.shape )

        
    # ------------------------------------------------- #
    # --- generate image Type Data                  --- #
    # ------------------------------------------------- #
    def generate__imageData( self, shape=None, Origin=[0.0,0.0,0.0], Spacing=[1,1,1] ):

        self.imageData      = []
        self.nImageData     = 0
        self.Origin         = Origin
        self.Spacing        = Spacing
        
        # ------------------------------------------------- #
        # --- [1] image case ; copy it                  --- #
        # ------------------------------------------------- #
        if   ( self.DataType == "image"      ):
            self.imageData  = [ self.Data ]
            self.nImageData = 1
            return()
        # ------------------------------------------------- #
        # --- [2] 1darray case                          --- #
        # ------------------------------------------------- #
        if ( self.DataType == "1darray" ):
            self.imageData  = []
            self.nImageData = 0
            if ( self.shape is not None ):
                if ( len( self.shape ) >= 2 ):
                    self.imageData  = [ np.reshape( self.Data, self.shape ) ]
                    self.nImageData = 1
            else:
                print( "[generate__imageData -@vtkDataUnit-] self.shape is None [ERROR]" )
                print( "[generate__imageData -@vtkDataUnit-] self.DataType == 1darray "  )
                print( "[generate__imageData -@vtkDataUnit-]    cannot generate imageData..." )
            return()
        # ------------------------------------------------- #
        # --- [3] point case                            --- #
        # ------------------------------------------------- #
        if ( self.DataType == "point" ):
            # -- [3-1] shape check ; if not exist error --  #
            if ( shape  is not None ): self.shape = shape
            if ( self.shape is None ):
                sys.exit( "[generate__imageData -@generate__imageData-] self.shape == ??? " )
            # -- [3-2] store imageData                  --  #
            self.imageData  = []
            if ( self.DataOrder == "ijk" ):
                for ik in range( self.nComponents ):
                    self.imageData.append( np.reshape( self.Data[...,ik], self.shape[:-1] ) )
            if ( self.DataOrder == "kji" ):
                for ik in range( self.nComponents ):
                    self.imageData.append( np.reshape( self.Data[ik,...], self.shape[1: ] ) )
            self.nImageData = len( self.imageData )
            return()
        # ------------------------------------------------- #
        # --- [4] structured case                       --- #
        # ------------------------------------------------- #
        if ( self.DataType == "structured" ):
            self.imageData  = []
            if ( self.DataOrder == "ijk" ):
                for ik in range( self.nComponents ):
                    self.imageData.append( self.Data[...,ik] )
            if ( self.DataOrder == "kji" ):
                for ik in range( self.nComponents ):
                    self.imageData.append( np.transpose( self.Data[ik,...] ) )
            self.nImageData = len( self.imageData )
            return()
        
    
    # ------------------------------------------------- #
    # --- generate__coordinateData                  --- #
    # ------------------------------------------------- #
    def generate__coordinateData( self, coordinates=None ):
        
        if ( self.pointData is None ): self.generate__pointData()
        self.set__coordinates( coordinates=coordinates )
        self.coordinateData  = self.pointData[:,self.coordinates]
        self.nCoordinates    = len( self.coordinates )
        self.coordinateLabel = [ self.DataLabel[ik] for ik in list( self.coordinates ) ]


    # ------------------------------------------------- #
    # --- generate__fieldData                      --- #
    # ------------------------------------------------- #
    def generate__fieldData( self, fields=None ):

        if ( self.pointData is None ): self.generate__pointData()
        self.set__fields( fields=fields )
        self.fieldData  = self.pointData[:,self.fields]
        self.nFields    = len( self.fields )
        self.fieldLabel = [ self.DataLabel[ik] for ik in list( self.fields ) ]
        
        
    # ------------------------------------------------- #
    # --- set coordinate for pointData              --- #
    # ------------------------------------------------- #
    def set__coordinates( self, coordinates=None ):
        
        if ( coordinates is not None ):
            self.coordinates = coordinates
        if ( self.coordinates is None ):
            self.coordinates = tuple( range( min( self.nComponents-1, 3 ) ) )

            
    # ------------------------------------------------- #
    # --- set index of field for pointData          --- #
    # ------------------------------------------------- #
    def set__fields( self, fields=None ):
        
        if ( fields is not None ):
            self.fields = fields
        if ( self.coordinates is None ):
            self.set__coordinates()
        if ( self.fields is None ):
            allindex    = tuple( range( self.nComponents ) )
            self.fields = tuple( set( allindex ) - set( self.coordinates ) )

    
            
        
# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ 0.0, 1.0, 11 ]
    x2MinMaxNum = [ 0.0, 1.0, 11 ]
    x3MinMaxNum = [ 0.0, 1.0, 11 ]
    data1       = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "point" )
    
    vtkData = vtkDataUnit( Data=data1, tag="data1", shape=(11,11,11,3) )
    info    = vtkData.inspect__inputData()
    vtkData.generate__pointData()
    vtkData.generate__structuredData()
    vtkData.generate__imageData()
    vtkData.generate__coordinateData()
    vtkData.generate__fieldData()
    
    print( vtkData.pointData.shape )
    for img in vtkData.imageData:
        print( img.shape )
    print( vtkData.nImageData )
    print( vtkData.coordinates )
    print( vtkData.coordinateData.shape )
    print( vtkData.fields )
    print( vtkData.fieldData.shape )
    print( info )
