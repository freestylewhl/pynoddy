'''Noddy output file analysis
Created on 24/03/2014

@author: Florian Wellmann
'''

import numpy as np
import matplotlib.pyplot as plt

class NoddyOutput(object):
    """Class definition for Noddy output analysis"""
    
    def __init__(self, output_name):
        """Noddy output analysis
        
        **Arguments**:
            - *output_name* = string : (base) name of Noddy output files
        """
        self.basename = output_name
        self.load_model_info()
        self.load_geology()
        
    def __add__(self, other):
        """Define addition as addition of grid block values
        
        Note: Check first if model dimensions and settings are the same
        """
        # check dimensions
        self.compare_dimensions_to(other)
        # 1. create copy
        import copy
        tmp_his = copy.deepcopy(self)
        # 2. perform operation
        tmp_his.block = self.block + other.block
        return tmp_his

    def __sub__(self, other):
        """Define subtraction as subtraction of grid block values
        
        Note: Check first if model dimensions and settings are the same
        """
        # check dimensions
        self.compare_dimensions_to(other)
        # 1. create copy
        import copy
        tmp_his = copy.deepcopy(self)
        # 2. perform operation
        tmp_his.block = self.block - other.block
        return tmp_his

    def __iadd__(self, x):
        """Augmented assignment addtition: add value to all grid blocks
        
        **Arguments**:
            - *x*: can be either a numerical value (int, float, ...) *or* another
            NoddyOutput object! Note that, in both cases, the own block is updated
            and no new object is created (compare to overwritten addition operator!)
        
        Note: This method is changing the object *in place*!
        """
        # if x is another pynoddy output object, then add values to own grid in place!
        if isinstance(x, NoddyOutput):
            self.block += x.block
        else:
            self.block += x
        # update grid values
        
        return self

    def __isub__(self, x):
        """Augmented assignment addtition: add value(s) to all grid blocks
        
        **Arguments**:
            - *x*: can be either a numerical value (int, float, ...) *or* another
            NoddyOutput object! Note that, in both cases, the own block is updated
            and no new object is created (compare to overwritten addition operator!)
        
        Note: This method is changing the object *in place*!
        """
        # if x is another pynoddy output object, then add values to own grid in place!
        if isinstance(x, NoddyOutput):
            self.block -= x.block
        else:
            self.block -= x
        # update grid values
        
        return self
    
    def set_basename(self, name):
        """Set model basename"""
        self.basename = name
        
        
    def compare_dimensions_to(self, other):
        """Compare model dimensions to another model"""
        try:
            assert((self.nx, self.ny, self.nz) == (other.nx, other.ny, other.nz))
        except AssertionError:
            raise AssertionError("Model dimensions do not seem to agree, please check!\n")
        try:
            assert((self.delx, self.dely, self.delz) == (other.delx, other.dely, other.delz))
        except AssertionError:
            raise AssertionError("Model dimensions do not seem to agree, please check!\n")
        try:
            assert((self.xmin, self.ymin, self.zmin) == (other.xmin, other.ymin, other.zmin))
        except AssertionError:
            raise AssertionError("Model dimensions do not seem to agree, please check!\n")
        
    def load_model_info(self):
        """Load information about model discretisation from .g00 file"""
        filelines = open(self.basename + ".g00").readlines() 
        for line in filelines:
            if 'NUMBER OF LAYERS' in line:
                self.nz = int(line.split("=")[1])
            elif 'LAYER 1 DIMENSIONS' in line:
                (self.nx, self.ny) = [int(l) for l in line.split("=")[1].split(" ")[1:]]
            elif 'UPPER SW CORNER' in line:
                l = [float(l) for l in line.split("=")[1].split(" ")[1:]]
                (self.xmin, self.ymin, self.zmax) = l
            elif 'LOWER NE CORNER' in line:
                l = [float(l) for l in line.split("=")[1].split(" ")[1:]]
                (self.xmax, self.ymax, self.zmin) = l
            elif 'NUM ROCK' in line:
                self.n_rocktypes = int(line.split('=')[1])
        self.n_total = self.nx * self.ny * self.nz
        (self.extent_x, self.extent_y, self.extent_z) = (self.xmax - self.xmin, self.ymax - self.ymin, 
                                                         self.zmax - self.zmin)
        (self.delx, self.dely, self.delz) = (self.extent_x / float(self.nx), 
                                             self.extent_y / float(self.ny),
                                             self.extent_z / float(self.nz))
    
    
    def load_geology(self):
        """Load block geology ids from .g12 output file"""
        f = open(self.basename + ".g12")
        method = 'standard' # standard method to read file
        # method = 'numpy'    # using numpy should be faster - but it messes up the order... possible to fix?
        if method == 'standard':
            i = 0
            j = 0
            k = 0
            self.block = np.ndarray((self.nx,self.ny,self.nz))
            for line in f.readlines():
                if line == '\n':
                    # next z-slice
                    k += 1
                    # reset x counter
                    i = 0
                    continue
                l = [int(l1) for l1 in line.strip().split("\t")]
                self.block[i,:,self.nz-k-1] = np.array(l)[::-1]
                i += 1
              
        
        elif method == 'standard_old':
            j = 0 
            j_max = 0
            k_max = 0
            i_max = 0
            self.block = np.ndarray((self.nz,self.ny,self.nx))
            for k,line in enumerate(f.readlines()):
                if line == '\n':
                    # next y-slice
                    j += 1
                    if j > j_max : j_max = j
                    continue
                for i,l1 in enumerate(line.strip().split("\t")):
                    if i > i_max: i_max = i
                    if k/self.nz > k_max : k_max = k/self.nz
                    self.block[j,i,k/self.nz-1] = int(l1)
            print i_max, j_max, k_max
                    
        
        elif method == 'numpy':
            # old implementation - didn't work, but why?
            self.block = np.loadtxt(f, dtype="int")
            # reshape to proper 3-D shape
            self.block = self.block.reshape((self.nz,self.ny,self.nx))
            self.block = np.swapaxes(self.block, 0, 2)
            # self.block = np.swapaxes(self.block, 0, 1)
            # print np.shape(self.block)
    
    def determine_unit_volumes(self):
        """Determine volumes of geological units in the discretized block model
        
        """
        #
        # Note: for the time being, the following implementation is extremely simple
        # and could be optimised, for example to test specifically for units defined
        # in stratigraphies, intrusions, etc.!
        # 
        self.block_volume = self.delx * self.dely * self.delz
        self.unit_ids = np.unique(self.block)
        self.unit_volumes = np.empty(np.shape(self.unit_ids))
        for i,unit_id in enumerate(self.unit_ids):
            self.unit_volumes[i] = np.sum(self.block == unit_id) * self.block_volume
        
        
        
    def plot_section(self, direction='y', position='center', **kwds):
        """Create a section block through the model
        
        **Arguments**:
            - *direction* = 'x', 'y', 'z' : coordinate direction of section plot (default: 'y')
            - *position* = int or 'center' : cell position of section as integer value
                or identifier (default: 'center')
        
        **Optional Keywords**:
            - *ax* = matplotlib.axis : append plot to axis (default: create new plot)
            - *figsize* = (x,y) : matplotlib figsize
            - *colorbar* = bool : plot colorbar (default: True)
            - *colorbar_orientation* = 'horizontal' or 'vertical' : orientation of colorbar
                    (default: 'vertical')
            - *title* = string : plot title
            - *savefig* = bool : save figure to file (default: show directly on screen)
            - *cmap* = matplotlib.cmap : colormap (default: YlOrRd)
            - *fig_filename* = string : figure filename
            - *ve* = float : vertical exaggeration
            - *layer_labels* = list of strings: labels for each unit in plot
            - *layers_from* = noddy history file : get labels automatically from history file
            - *data* = np.array : data to plot, if different to block data itself
        """
        cbar_orientation = kwds.get("colorbar_orientation", 'vertical')
        # determine if data are passed - if not, then recompute model
        if kwds.has_key("data"):
            data = kwds["data"]
        ve = kwds.get("ve", 1.)
        cmap_type = kwds.get('cmap', 'YlOrRd')
        if kwds.has_key('ax'):
            # append plot to existing axis
            ax = kwds['ax']
            return_axis = True
        else:
            return_axis = False
            figsize = kwds.get("figsize", (10,6))
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
        savefig = kwds.get("savefig", False)
        colorbar = kwds.get("colorbar", True)
            
        # extract slice
        if direction == 'x':
            if position == 'center':
                cell_pos = self.nx / 2
            else:
                cell_pos = position
            if kwds.has_key('data'):
                section_slice = data[cell_pos,:,:].transpose()
            else:
                section_slice = self.block[cell_pos,:,:].transpose()
            xlabel = "y"
            ylabel = "z"
        if direction == 'y':
            if position == 'center':
                cell_pos = self.ny / 2
            else:
                cell_pos = position
            if kwds.has_key('data'):
                section_slice = data[:,cell_pos,:].transpose()
            else:
                section_slice = self.block[:,cell_pos,:].transpose()
            xlabel = "x"
            ylabel = "z"
        if direction == 'z':
            if position == 'center':
                cell_pos = self.nz / 2
            else:
                cell_pos = position
            if kwds.has_key('data'):
                section_slice = data[:,:,cell_pos].transpose()
            else:
                section_slice = self.block[:,:,cell_pos].transpose()
            xlabel = "x"
            ylabel = "y"

        title = kwds.get("title", "Section in %s-direction, pos=%d" % (direction, cell_pos))
                
        im = ax.imshow(section_slice, interpolation='nearest', aspect=ve, cmap=cmap_type, origin = 'lower left')
        if colorbar:
#            cbar = plt.colorbar(im)
#            _ = cbar
#        
            import matplotlib as mpl
            bounds = np.arange(np.min(section_slice),np.max(section_slice)+1)
            cmap = plt.cm.jet
            norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
            if cbar_orientation == 'horizontal':
                ax2 = fig.add_axes([0.125, 0.18, 0.775, 0.04])
                cb = mpl.colorbar.ColorbarBase(ax2, cmap=cmap_type, norm=norm, spacing='proportional', 
                                           ticks=bounds-0.5, boundaries=bounds,
                                           orientation = 'horizontal') # , format='%s')
                
            else: # default is vertical 
                # create a second axes for the colorbar
                ax2 = fig.add_axes([0.95, 0.165, 0.03, 0.69])
                cb = mpl.colorbar.ColorbarBase(ax2, cmap=cmap_type, norm=norm, spacing='proportional', 
                                           ticks=bounds-0.5, boundaries=bounds,
                                           orientation = 'vertical') # , format='%s')
            # define the bins and normalize
    
            if kwds.has_key("layer_labels"):
                cb.set_ticklabels(kwds["layer_labels"])
                
            # invert axis to have "correct" stratigraphic order
            cb.ax.invert_yaxis()

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        if return_axis:
            return ax
        elif savefig:
            fig_filename = kwds.get("fig_filename", "%s_section_%s_pos_%d" % (self.basename, direction, cell_pos))
            plt.savefig(fig_filename, bbox_inches="tight")
        else:
            plt.show()
            
    def export_to_vtk(self, **kwds):
        """Export model to VTK
        
        Export the geology blocks to VTK for visualisation of the entire 3-D model in an
        external VTK viewer, e.g. Paraview.
        
        ..Note:: Requires pyevtk, available for free on: https://github.com/firedrakeproject/firedrake/tree/master/python/evtk
        
        **Optional keywords**:
            - *vtk_filename* = string : filename of VTK file (default: output_name)
            - *data* = np.array : data array to export to VKT (default: entire block model)
        """
        vtk_filename = kwds.get("vtk_filename", self.basename)
        
        from evtk.hl import gridToVTK
        # Coordinates
        x = np.arange(0, self.extent_x + 0.1*self.delx, self.delx, dtype='float64')
        y = np.arange(0, self.extent_y + 0.1*self.dely, self.dely, dtype='float64')
        z = np.arange(0, self.extent_z + 0.1*self.delz, self.delz, dtype='float64')
        
        # self.block = np.swapaxes(self.block, 0, 2)
        
        if kwds.has_key("data"):
            gridToVTK(vtk_filename, x, y, z, cellData = {"data" : kwds['data']})         
        else:
            gridToVTK(vtk_filename, x, y, z, cellData = {"geology" : self.block})         
        
class NoddyGeophysics(object):
    """Definition to read, analyse, and visualise calculated geophysical responses"""
     
    def __init__(self, output_name):
        """Methods to read, analyse, and visualise calculated geophysical responses
         
        .. note:: The geophysical responses have can be computed with a keyword in the
        function `compute_model`, e.g.:
        ``pynoddy.compute_model(history_name, output, type = 'GEOPHYSICS')``
        """
        self.basename = output_name
        self.read_gravity()
        self.read_magnetics()
         
    def read_gravity(self):
        """Read calculated gravity response"""
        grv_lines = open(self.basename + ".grv", 'r').readlines()
        self.grv_header = grv_lines[:8]
        # read in data
        # print len(grv_lines) - 8
        dx = len(grv_lines) - 8
        dy = len(grv_lines[8].rstrip().split("\t"))
        self.grv_data = np.ndarray((dx, dy))
        for i,line in enumerate(grv_lines[8:]):
            self.grv_data[i,:] = np.array([float(x) for x in line.rstrip().split("\t")])
            
    def read_magnetics(self):
        """Read caluclated magnetic field response"""
        mag_lines = open(self.basename + ".mag", 'r').readlines()
        self.mag_header = mag_lines[:8]
        # read in data
        # print len(mag_lines) - 8
        dx = len(mag_lines) - 8
        dy = len(mag_lines[8].rstrip().split("\t"))
        self.mag_data = np.ndarray((dx, dy))
        for i,line in enumerate(mag_lines[8:]):
            self.mag_data[i,:] = np.array([float(x) for x in line.rstrip().split("\t")])


class NoddyTopology(object):
    """Definition to read, analyse, and visualise calculated voxel topology"""        
    def __init__(self, output_name):
        """Methods to read, analyse, and visualise calculated voxel topology
        .. note:: The voxel topology have can be computed with a keyword in the
        function `compute_model`, e.g.: ``pynoddy.compute_model(history_name, output, type = 'TOPOLOGY')``
        
        **Arguments**
         - *output_name* = the name of the noddy output to run topology on. Note that this output must end with
                           _0001.* in order to process correctly (TODO: fix this in topology.c code).
        """
        self.basename = output_name
        
        #load network
        self.loadNetwork()
        
    def loadNetwork(self):
        '''
        Loads the topology network into a NetworkX datastructure
        '''
        
        #import networkx
        try:
            import networkx as nx
        except ImportError:
            print "Warning: NetworkX module could not be loaded. Please install NetworkX from https://networkx.github.io/ to perform topological analyses in PyNoddy"
        
        #initialise new networkX graph
        self.graph = nx.Graph()
        self.graph.name = self.basename

        #load lithology properties
        self.read_properties()
               
        #load graph
        f = open(self.basename + ".g23",'r')
        lines = f.readlines() #read lines
        
        for l in lines: #load edges
            l=l.rstrip()
            data=l.split('\t')
    
            #calculate edge colors
            topoCode1 = data[0].split('_')[1]
            topoCode2 = data[1].split('_')[1]
            lithoCode1 = data[0].split('_')[0]
            lithoCode2 = data[1].split('_')[0]
            count = int(data[-1]) #number of voxels with this neibour relationship (proxy of surface area)
            
            #calculate edge type (dyke, fault etc)
            eCode=0
            eType = 'stratigraphic' #default is stratigraphy
            eColour='k' #black
            for i in range(0,len(topoCode1) - 1): #-1 removes the trailing character
                if (topoCode1[i] != topoCode2[i]): #find the difference
                    if int(topoCode2[i]) > int(topoCode1[i]):
                        eCode=topoCode2[i]
                    else:
                       eCode=topoCode1[i]
                       
                    if int(eCode) == 0: #stratigraphic contact
                        eColour = 'k' #black
                        eType = 'stratigraphic'
                    elif int(eCode) == 2 or int(eCode) == 7 or int(eCode) == 8: #various types of faults
                        eColour = 'r' #red
                        eType = 'fault'
                    elif int(eCode) == 3: #unconformity
                        eColour = 'b' #blue
                        eType = 'unconformity'
                    elif int(eCode) == 5: #plug/dyke
                        eColour = 'y' #yellow
                        eType = 'intrusive'
                    else:
                        eColour = 'g' #green
                        eType = 'unknown' 
            
            #create nodes & associated properties
            self.graph.add_node(data[0], lithology=lithoCode1, name=self.lithology_properties[int(lithoCode1)]['name'])
            self.graph.node[data[0]]['colour']=self.lithology_properties[int(lithoCode1)]['colour']
            self.graph.node[data[0]]['centroid']=self.node_properties[ "%d_%s" % (int(lithoCode1),topoCode1) ]['centroid']
            self.graph.node[data[0]]['volume'] = self.node_properties[ "%d_%s" % (int(lithoCode1),topoCode1) ]['volume']
            
            self.graph.add_node(data[1], lithology=lithoCode2, name=self.lithology_properties[int(lithoCode2)]['name'])
            self.graph.node[data[1]]['colour']=self.lithology_properties[int(lithoCode2)]['colour']
            self.graph.node[data[1]]['centroid']=self.node_properties[ "%d_%s" % (int(lithoCode2),topoCode2) ]['centroid']
            self.graph.node[data[1]]['volume'] = self.node_properties[ "%d_%s" % (int(lithoCode2),topoCode2) ]['volume']
           
            #add edge
            self.graph.add_edge(data[0],data[1],edgeCode=eCode,edgeType=eType, colour=eColour, area=count, weight=1)
    
    def read_properties( self ):
        
        #initialise properties dict
        self.lithology_properties = {}
        
        #open & parse properties file
        f = open(self.basename + ".g20", 'r')
        lines = f.readlines()   
        nevents = int(lines[0].split(' ')[2]) #number of events
    
        for i in range(nevents + 3,len(lines)): #loop through lithology definitions
            l = (lines[i].strip()).split(' ')
        
            #load lithology parameters
            params = {}
            params['code'] = int(l[0])
            params['name'] = ' '.join(l[2:-3])
            #colours are the last 3 values
            params['colour'] = [ float(l[-3]) / 255.0, float(l[-2]) / 255.0, float(l[-1]) / 255.0 ]
        
            #store lithology parameters (using lithocode as key)
            self.lithology_properties[params['code']] = params
            
        #close properties file
        f.close
        
        #load node locations from .vs file
        self.node_properties = {}
        f = open(self.basename + "_v.vs", 'r')
        lines =f.readlines()
        for l in lines:
            if "PVRTX" in l: #this is a vertex
                data = l.split(' ')
                params = {}
                params['centroid']=[ float(data[2]), float(data[3]), float(data[4])]
                params['litho'] = int(data[5])
                params['topo'] = data[6]
                params['volume'] = int(data[7]) #number of voxels of this type
                
                #save (key = LITHO_TOPO (eg. 2_001a))
                self.node_properties[ '%d_%s' % (params['litho'],params['topo']) ] = params
        f.close()
        
    def read_adjacency_matrix(self):
        """**DEPRECIATED**
        Read max number of lithologies aross all models"""
        ml_lines = open(self.basename + ".g22", 'r').readlines()
        # read in data
        
        for line in ml_lines:
            self.maxlitho = line 
            
        print "maxlitho =", self.maxlitho
    
    def filter_node_volumes(self,min_volume=50):
        '''
        Removes all nodes with volumes less than the specified size
        
        **Arguments**:
         - *min_volume* = the threshold volume. Nodes with smaller volumes are deleted.
         
        **Returns**
         - returns the number of deleted nodes
        '''
        
        count = 0
        for n in self.graph.nodes():
            if self.graph.node[n]['volume'] < min_volume:
                self.graph.remove_node(n)
                count+=1
        
        return count
    
    def jaccard_coefficient(self,G2):
        '''
        Calculates the Jaccard Coefficient (ratio between the intersection & union) of the graph representing this NOddyTopology and G2.
        
        **Arguments**
         - *G2* = a valid NoddyTopology object or NetworkX graph that this topology is to be compared with
         
        **Returns**
          - The jaccard_coefficient
        '''
        
        intersection=0
        union=self.graph.number_of_edges()
        
        #ensure G2 is a graph object
        if isinstance(G2,NoddyTopology):
            G2 = G2.graph #we want the graph bit
        
        for e in self.graph.edges_iter():
            if (G2.has_edge(e[0],e[1])): #edge is shared
                intersection+=1
            else: #edge is new, add to union
                union += 1
        return intersection / float(union)

    def is_unique(self, known ):
        '''
        Returns True if the topology of this model is different (ie. forms a different network) to a list of models.
        
        **Arguments**:
            -*known* = a list of valid NoddyTopology objects or NetworkX graphs to compare with.
        
        **Returns**:
         - Returns true if this topology is unique, otherwise false
        '''
        for g2 in known:
            if self.jaccard_coefficient(g2) == 1:
                return False #the models match
        return True
    
    @staticmethod
    def calculate_unique_topologies(topology_list, **kwds):
        '''
        Calculates the number of unique topologies in a list of NoddyTopologies
        
        **Arguments**:
         - *topology_list* = The list of NoddyTopologies to search through.
         
        **Optional Keywords**:
         - *output* = File to write cumulative observed topologies distribution. Default is None (nothing written).
        
        **Returns**:
         - Returns a list of unique topologies.
       '''
        
        output = kwds.get("output",None)
        
        if not output is None:
            f = open(output,'w')
        
        uTopo = []
        for t in topology_list:
            if t.is_unique(uTopo):
                #t.filter_node_volumes(50)
                uTopo.append(t)
            
            #write cumulative output
            if not output is None:
                f.write("%d\n" % len(uTopo))
                
        #close output
        if not output is None:
            f.close()
            
        return uTopo
        
    def calculate_overlap(self, G2):
        '''
        Calculates the overlap between this NoddyTopology and another NoddyTopology or networkX graph
        
        **Arguments**
         - *G2* = a valid NoddyTopology object or NetworkX graph that this topology is to be compared with
         
        **Returns**
          - The number of overlapping edges 
          
        '''
        
        #ensure G2 is a graph object
        if (isinstance(G2,NoddyTopology)):
            G2 = G2.graph #we want the graph bit
        
        similarity=0
        for e in self.graph.edges_iter():
            if (G2.has_edge(e[0],e[1])):
                similarity+=1
        return similarity
        
        
    def find_matching(self,known):
        '''
        Finds the first matching NoddyTopology (or NetworkX graph) in the specified list
        
        **Arguments**:
            -*known* = a list of valid NoddyTopology objects or NetworkX graphs to compare with.
        
        **Returns**:
         - Returns the first matching object (jaccard coefficient = 1), or otherwise None
        
        '''
        for g1 in known:
            if self.jaccard_coefficient(g1) == 1.0:
                return g1 #return the match
        return None #no match
       
    def draw_matrix_image( self, outputname="" ):
        '''
        Draws an (adjacency) matrix representing this NoddyTopology object.
        
        **Arguments**
         - *outputname* = the path of the image to be written. If left as '' the image is written to the same directory as the basename.
        '''
        
        #try importing matplotlib
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print ("Could not draw image as matplotlib is not installed. Please install matplotlib")
            
        #get output path
        if outputname == "":
            outputname = self.basename + "_matrix.jpg"
            
        #open the matrix file
        f = open(self.basename + '.g25','r')
        lines = f.readlines()
        rows = []
        for l in lines:
            l = l.rstrip()
            row = []
            for e in l.split('\t'):
                row.append(int(e))
            rows.append(row)
    
        #draw & save
        print "Saving matrix image to... " + outputname
        cmap=plt.get_cmap('Paired')
        cmap.set_under('white')  # Color for values less than vmin
        plt.imshow(rows, interpolation="nearest", vmin=1, cmap=cmap)
        plt.savefig(outputname)
        plt.clf()
    
    def draw_network_image(self, outputname="", **kwds ):
        '''
        Draws a network diagram of this NoddyTopology to the specified image
        
        **Arguments**
         - *outputname* = the path of the image being written. If left as '' the image is written to the same directory as the basename.
        **Optional Keywords**
         - *dimension* = '2D' for a 2D network diagram or '3D' for a 3D network diagram. Default is '2D'.
         - *axis* = the axis to view on for 3D network diagrams
         - *perspective* = True to use perspective projection, or False for orthographic projection. Default is False.
         - *node_size* = The size that nodes are drawn. Default is 1500.
         - *layout* = The layout algorithm used in 2D. Options are 'spring_layout' (default), 'shell_layout', 'circular_layout' 
                      and 'spectral_layout'.
         - *verbose* = True if this function is allowed to write to the print buffer, otherwise false. Default is true
        '''
        
        #import networkx
        import networkx as nx
        
        #try importing matplotlib
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print ("Could not draw image as matplotlib is not installed. Please install matplotlib")
            
            
        #get args
        dims=kwds.get("dimension",'2D')    
        view_axis=kwds.get("axis",'y') #default view along y axis
        perspective=kwds.get("perspective",False)
        node_size = kwds.get("node_size",1500)
        layout = kwds.get("layout",'spring_layout')
        verbose = kwds.get("verbose",True)
        
        #get output path
        if outputname == "":
            outputname = self.basename + "_graph.jpg"
        
        #setup node colours (by lithologies)
        #nCols = map(int,[G.node[n]['lithology'] for n in G.nodes()])
        nCols = []
        for n in self.graph.nodes():
            nCols.append(self.graph.node[n]['colour'])
            
        #setup colors (by type)
        eCols = []#map(int,[G.edge[e[0]][e[1]]['edgeType'] for e in G.edges()])
        for e in self.graph.edges():
            eCols.append(self.graph.edge[e[0]][e[1]]['colour'])
        
        
        #calculate node positions & sizes
        size = [node_size] * nx.number_of_nodes(self.graph)
        pos = {}
        
        if '3D' in dims: #3D layout
            size_dict = {}
            for n in self.graph.nodes():
                #initialise size array
                size_dict[n] = node_size
                dz=1 #z buffer
                
                #calculate 2D location (orthographic)
                if view_axis == 'x' or view_axis == 'side': #side view
                    pos[n]=[self.graph.node[n]['centroid'][1],self.graph.node[n]['centroid'][2]]
                    dz=self.graph.node[n]['centroid'][0]
                elif view_axis == 'y' or view_axis == 'front': #front view
                    pos[n]=[self.graph.node[n]['centroid'][0],self.graph.node[n]['centroid'][2]]
                    dz=self.graph.node[n]['centroid'][1]
                elif view_axis == 'z' or view_axis == 'top': #top view
                    pos[n]=[self.graph.node[n]['centroid'][0],self.graph.node[n]['centroid'][1]]
                    dz=self.graph.node[n]['centroid'][2]
                
                #apply perspective correction if necessary
                if perspective==True:
                    pos[n][0] = pos[n][0] / (dz)
                    pos[n][1] = pos[n][1] / (dz)
                    size_dict[n] = (size_dict[n] / dz) * 500
                
            #store size array
            size = size_dict.values()
            
        else: #2D layout
            if 'shell_layout' in layout: #layouts: spring_layout, shell_layout, circular_layout, spectral_layout
                pos = nx.shell_layout(self.graph)
            if 'circular_layout' in layout:
                pos = nx.circular_layout(self.graph)
            if 'circular_layout' in layout:
                pos = nx.spectral_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)
            
        #print "Position = " + str(pos)
        
        #draw & save
        if verbose:
            print "Saving network image to..." + outputname
        
        nx.draw(self.graph,pos,node_color=nCols,node_size=size, edge_color=eCols) #cmap=cm
        
        #nx.draw_networkx_labels(G,pos,font_size=8)
        
        plt.savefig(outputname)
        plt.clf()
    def draw_3d_network( self, **kwds ):
        '''
        Draws a 3D network using Mayavi.
        
        **Optional Keywords**:
         - *show* = If True, the 3D network is displayed immediatly on-screen in an
                    interactive mayavi viewer. Default is True.
         - *output* = If defined an image of the network is saved to this location.
         - *vtk* = A path to save a .vtk model of the network (for later viewing). If
                   undefined a vtk is not saved (default)
        '''
        
        #import mayavi & networkx
        import networkx as nx
        
        try:
            from mayavi import mlab
            import numpy as np
        except:
            print("Error drawing interactive network: Mayavi is not installed")
            return
        
        show = kwds.get("show",True)
        outputname = kwds.get("output",'')
        vtk = kwds.get("vtk",'')
        
        #convert node labels to integers
        G2 = nx.convert_node_labels_to_integers(self.graph)
        
        #load positions
        x = []
        y = []
        z = []
        nCols = []
        for n in G2.nodes():
            x.append(G2.node[n]['centroid'][0])
            y.append(G2.node[n]['centroid'][1])
            z.append(G2.node[n]['centroid'][2])
            nCols.append(int(G2.node[n]['lithology']))
        
        #make figure
        mlab.figure(1, bgcolor=(1,1,1))
        mlab.clf()
        
        pts = mlab.points3d(x,y,z,nCols, scale_factor=250, scale_mode='none',resolution=20)
    
        pts.mlab_source.dataset.lines = np.array(G2.edges())
        tube = mlab.pipeline.tube(pts,tube_radius=10)
        mlab.pipeline.surface(tube,color=(0.3,0.3,0.3))
        
        #show
        if show:
            mlab.show()
            
        #save
        if outputname != '':
            mlab.savefig(outputname)
        
        if vtk!='':
            try:
                from tvtk.api import write_data
            except:
                print("Warning: tvtk not installed - cannot write vtk file.")
                return
    
            write_data(pts.mlab_source.dataset,outputname)
        
if __name__ == '__main__':
    # some testing and debugging functions...
    import os
#     os.chdir(r'/Users/Florian/git/pynoddy/sandbox')
#     NO = NoddyOutput("strike_slip_out")
    os.chdir('C:/Users/Sam/SkyDrive/Documents/Masters/Models/Primitive/Fold+Unconformity+Intrusion+Fault/vary_fault_dip_only/12476/2')
    NO = "out_0001"
    
    #create NoddyTopology
    topo = NoddyTopology(NO)
    
    #draw network
    topo.draw_network_image(dimension='3D',perspective=False,axis='x')
    
    #draw matrix
    topo.draw_matrix_image()
    
    #draw 3D network
    topo.draw_3d_network()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
