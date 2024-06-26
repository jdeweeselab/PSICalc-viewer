from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QAction
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from ps_app.views.csv_view import ClusterData
from mpl_toolkits.axes_grid1 import make_axes_locatable

import networkx as nx
import numpy as np
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt


class ApplicationWindow(QtWidgets.QMainWindow):
    """Tree Window View"""
    def __init__(self, cluster_map, msa, low_entropy, column_map):
        super().__init__()
        self.cluster_map = cluster_map
        self.msa = msa
        self.low_entropy = low_entropy
        self.column_map = column_map

        self.lines = [[str(k), str(v[0]), str(v[1])] for k, v in self.cluster_map.items()]

        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        self.draw_tree(0)

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.tabs = QtWidgets.QTabWidget()
        layout = QtWidgets.QVBoxLayout(self._main)

        self.table = ClusterData(self.cluster_map, self.msa, self.low_entropy, self.column_map)
        self.tabs.addTab(self.canvas, "Tree View")
        self.tabs.addTab(self.table, "Cluster Data")
        layout.addWidget(self.tabs)
        self.nav_bar = self.addToolBar(NavigationToolbar(self.canvas, self))

        save_file_action = QAction(QtGui.QIcon(":icons/excel_logo.png"), 'Save Excel', self)
        save_file_action.triggered.connect(self.table.save_sheet)
        self.toolbar = self.addToolBar('Data')
        self.toolbar.addAction(save_file_action)

        self.primeSpinBox = QtWidgets.QDoubleSpinBox()
        self.primeSpinBox.setRange(0.00, 1.00)
        self.primeSpinBox.setSingleStep(0.01)
        self.primeSpinBox.setValue(0.00)
        self.primeSpinBox.setGeometry(QtCore.QRect(90, 320, 42, 22))
        self.primeSpinBox.setObjectName("primeSpinBox")
        self.primeSpinBox.valueChanged.connect(self.primeSpinBox_handler)
        self.toolbar.addWidget(self.primeSpinBox)

    def primeSpinBox_handler(self):
        prime_cluster_val = round(self.primeSpinBox.value(), 3)
        self.draw_tree(prime_cluster_val)
        self.canvas.draw()

    # reformats sequence of numbers with hyphens
    def get_line_numbers_concat(self, line_nums):
        seq = []
        final = []
        last = 0

        for index, val in enumerate(line_nums):

            if last + 1 == val or index == 0:
                seq.append(self.column_map.get(val))
                last = val
            else:
                if len(seq) > 1:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq) - 1]))
                else:
                    final.append(str(seq[0]))
                seq = list()
                seq.append(self.column_map.get(val))
                last = val

            if index == len(line_nums) - 1:
                if len(seq) > 1:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq) - 1]))
                else:
                    final.append(str(seq[0]))

        final_str = ', '.join(map(str, final))
        final_str = ''.join(('(', final_str, ')'))
        return final_str

    @staticmethod
    def calculate_node_size(x):
        return np.rint(90 / (np.log10(x)))

    def draw_tree(self, cutoff):
        """
        This is the main tree drawing method
        """

        data = [e for e in self.lines if len(e) != 0]
        values = [entry for entry in data if float(entry[1]) >= cutoff]  # modified variable
        tree_list = [(entry[0].strip('()'), entry[1]) for entry in values]
        tree_list = [(i[0].split(','), i[1]) for i in tree_list]
        reverse_column_map = {str(v): k for k, v in self.column_map.items()}
        tree_list = [
            (list(map(lambda a: reverse_column_map.get(a.strip().replace("'", "")), i[0])), float(i[1]))
            for i in tree_list
        ]
        max_len = max([len(s[0]) for s in tree_list])

        # Create graph and set default attributes for nodes
        attrs = {}
        G = nx.Graph()
        for node in G.nodes:
            attrs[node] = {'node': node, 'parent': False, 'sr_mode': None}
        nx.set_node_attributes(G, attrs)

        n_order = 1
        while n_order < max_len:

            n_order += 1
            next_set = [(s[0], s[1]) for s in tree_list if len(s[0]) == n_order]
            next_set = [(tuple(t[0]), t[1]) for t in next_set]
            next_set = sorted(list(set(next_set)))

            for i in next_set:
                G.add_node(i[0], parent=False, sr_mode=i[1])

            # Draw edges between nodes
            for i in G.nodes:
                if G.nodes[i]['parent'] is not True:
                    for j in G.nodes:
                        if i != j and set(i).issubset(set(j)):
                            G.add_edge(i, j)
                            G.nodes[i]['parent'] = True

        for v, w in G.edges:
            if G.nodes[v]["parent"] is True:
                G.edges[v, w]["subset"] = True
            else:
                G.edges[v, w]["subset"] = False

        # -------Node Positioning Calculator----------
        y_pos = 1000
        n_order = 1
        ytick_list = list()
        xtick_list = list()
        xtick_labels = list()
        ytick_labels = list()
        max_node_len = max([len(s) for s in G.nodes])

        while n_order < max_node_len:
            n_order += 1
            next_set = [s for s in G.nodes if len(s) == n_order]
            # Set x tick labels to identify pairwise cluster locations
            if n_order == 2:
                xtick_labels = [(next_set.index(x) + 1) for x in next_set]
            if len(next_set) != 0:
                # Set Y axis
                ytick_labels.append(str(n_order))
                y_pos -= 100
                ytick_list.append([y_pos, n_order])

        # On Windows, pygraphviz can't seem to hash arbitrary nodes, e.g., (19, 53). So we
        # create a mapping, relabel, call graphviz_layout(), and then relabel back to the
        # original...
        keys_as_int = {}
        keys_as_str = {}
        for i, label in enumerate(G):
            keys_as_int[label] = i
            keys_as_str[i] = label
        nx.relabel_nodes(G, keys_as_int, copy=False)
        pos = graphviz_layout(G, prog='dot')
        nx.relabel_nodes(G, keys_as_str, copy=False)

        for i, j in ytick_list:
            for each, coord in pos.items():
                if len(keys_as_str[each]) == j:
                    pos[each] = (coord[0], (i + 3))
        x_label = 1
        for each, coord in pos.items():
            if len(keys_as_str[each]) == 2:
                xtick_list.append(coord[0])
                x_label += 1

        pos = {self.get_line_numbers_concat(keys_as_str[k]): v for k, v in pos.items()}
        # noinspection PyTypeChecker
        G = nx.relabel_nodes(G, self.get_line_numbers_concat)

        """
        All of the custom graph drawing
        """
        self.fig.clear()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_ylabel('Order \n (n)', rotation=-0, fontsize=8, weight='bold')
        self.ax.yaxis.set_label_coords(0, 1.02)
        self.ax.set_xlabel('Site location in the Multiple Sequence Alignment', fontsize=8, weight='bold')
        self.ax.xaxis.set_label_coords(0.5, 1.12)
        self.ax.format_coord = lambda x, y: ""

        node_colors = [G.nodes[i]['sr_mode'] for i in G.nodes]
        node_scale_size = self.calculate_node_size(G.number_of_nodes())
        nodes = nx.draw_networkx_nodes(G, pos=pos, ax=self.ax, node_size=node_scale_size,
                                       node_color=node_colors, vmin=0.0, vmax=1.0, cmap=plt.cm.get_cmap('rainbow'))
        edges_p = [e for e in G.edges if G.edges[e]["subset"]]
        edges_s = [e for e in G.edges if not G.edges[e]["subset"]]
        nx.draw_networkx_edges(G, pos=pos, ax=self.ax, style='solid', edgelist=edges_p, edge_color='blue', alpha=.5)
        nx.draw_networkx_edges(G, pos=pos, ax=self.ax, style='dashed', edge_color='#DB7093', edgelist=edges_s, width=1.5,
                               alpha=.5)
        annot = self.ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                 bbox=dict(boxstyle="round", fc="w"),
                                 arrowprops=dict(arrowstyle="->"))
        flip_annot = self.ax.annotate("", xy=(0, 0), xytext=(-160, 20), textcoords="offset points",
                                      bbox=dict(boxstyle="round", fc="w"),
                                      arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        flip_annot.set_visible(False)
        avg_node_pos = np.mean(np.unique(
            sorted([v[0] for k, v in pos.items()])))

        idx_to_node_dict = {}
        for idx, node in enumerate(G.nodes):
            idx_to_node_dict[idx] = node

        def update_annot(ind):
            flip = False
            node_idx = ind["ind"][0]
            node = idx_to_node_dict[node_idx]
            xy = pos[node]
            annot.xy = xy
            if xy[0] >= avg_node_pos:
                flip = True
                flip_annot.xy = xy
            node_attr = {'cluster': node}
            node_attr.update(G.nodes[node])
            text = '\n'.join(f'{k}: {v}' for k, v in node_attr.items()
                             if k != "parent")
            if flip:
                flip_annot.set_text(text)
            else:
                annot.set_text(text)

            return flip

        def hover(event):
            vis1, vis2 = annot.get_visible(), flip_annot.get_visible()
            if event.inaxes == self.ax:
                cont, ind = nodes.contains(event)
                if cont:
                    decide_pos = update_annot(ind)
                    if decide_pos:
                        flip_annot.set_visible(True)
                    else:
                        annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                else:
                    if vis1 or vis2:
                        annot.set_visible(False)
                        flip_annot.set_visible(False)
                        self.fig.canvas.draw_idle()

        self.fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.grid(True, axis='y')

        divider = make_axes_locatable(plt.gca())
        cax = divider.append_axes("right", "2%", pad="3%")
        cb = plt.colorbar(nodes,
                          cax=cax,
                          orientation='vertical',
                          shrink=0.05,
                          pad=0.05
                          )
        cb.ax.set_title('SR(mode)', fontsize=8, weight='bold')

        y_ticks = [k for k, v in ytick_list]
        self.ax.yaxis.set_ticks(y_ticks)
        self.ax.yaxis.set_ticklabels(ytick_labels, visible=True)
        self.ax.xaxis.set_ticks(xtick_list)
        self.ax.xaxis.set_ticklabels(xtick_labels, visible=True)
        self.ax.tick_params(labelbottom=False, labeltop=False, labelleft=True, labelright=False, bottom=False,
                            top=False, left=False, right=False)
