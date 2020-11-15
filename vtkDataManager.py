import sys
import numpy                     as np
import nkVTKRoutines.vtkDataUnit as vdu


# ========================================================= #
# ===  vtkDataManager                                   === #
# ========================================================= #
class vtkDataManager():

    # ------------------------------------------------- #
    # --- vtk Data Manager Initialization         --- #
    # ------------------------------------------------- #
    def __init__( self, Data=None, tag=None, DataOrder=None, DataType=None, shape=None, \
                  DataLabel=None ):
        
        self.Data  = {}
        self.tags  = []

        if ( ( Data is not None ) and ( Data is not None ) ):
            self.add__vtkDataUnit( Data=Data, tag=tag, DataOrder=DataOrder, \
                                   DataType=DataType, shape=shape, DataLabel=DataLabel )

            
    # ------------------------------------------------- #
    # --- add vtk Data structure                    --- #
    # ------------------------------------------------- #
    def add__vtkDataUnit( self, Data=None, tag=None, DataOrder=None, DataType=None, \
                          DataLabel=None, shape=None ):
        self.Data[ tag ] = vdu.vtkDataUnit( Data=Data, tag=tag , shape   =shape, \
                                            DataOrder=DataOrder, DataType=DataType, \
                                            DataLabel=DataLabel )
        self.tags.append( tag ) 

        
    # ------------------------------------------------- #
    # --- show all vtk Data information             --- #
    # ------------------------------------------------- #
    def print__vtkDataInfo( self ):

        for tag in self.tags:
            print( self.Data[tag].inspect__inputData() )

            
    # ------------------------------------------------- #
    # --- generate pointData for all tags           --- #
    # ------------------------------------------------- #
    def generate__pointData( self ):
        
        for tag in self.tags:
            self.Data[tag].generate__pointData()

                
    # ------------------------------------------------- #
    # --- generate structuredData for all tags      --- #
    # ------------------------------------------------- #
    def generate__structuredData( self ):
        
        for tag in self.tags:
            self.Data[tag].generate__structuredData()

                
    # ------------------------------------------------- #
    # --- generate imageData for all tags           --- #
    # ------------------------------------------------- #
    def generate__imageData( self ):
        
        for tag in self.tags:
            self.Data[tag].generate__imageData()

                

# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    manager = vtkDataManager()
    
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum = [ 0.0, 1.0, 11 ]
    x2MinMaxNum = [ 0.0, 1.0, 11 ]
    x3MinMaxNum = [ 0.0, 1.0, 11 ]
    ret1        = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                     x3MinMaxNum=x3MinMaxNum, returnType = "structured" )
    manager.add__vtkDataUnit( Data=ret1, tag="ret1" )
    
    import nkUtilities.generate__testprofile as gtp
    x1MinMaxNum = [ 0.0, 1.0, 11 ]
    x2MinMaxNum = [ 0.0, 1.0, 11 ]
    x3MinMaxNum = [ 0.0, 1.0, 11 ]
    ret2        = gtp.generate__testprofile( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
    	                                     x3MinMaxNum=x3MinMaxNum, returnType = "point" )
    manager.add__vtkDataUnit( Data=ret2, tag="ret2",  )

    print()
    manager.print__vtkDataInfo()

