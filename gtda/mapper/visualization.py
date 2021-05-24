"""Static and interactive visualisation functions for Mapper graphs."""
# License: GNU AGPLv3

import logging
import traceback
from copy import deepcopy
from warnings import warn

import numpy as np
import plotly.graph_objects as go
from ipywidgets import widgets, Layout, HTML
from sklearn.base import clone

from .utils._logging import OutputWidgetHandler
from .utils._visualization import (
    _calculate_graph_data,
    _get_column_color_buttons,
    _get_colors_for_vals,
    PLOT_OPTIONS_LAYOUT_DEFAULTS
    )


def plot_static_mapper_graph(
        pipeline, data, layout="kamada_kawai", layout_dim=2,
        color_variable=None, node_color_statistic=None,
        color_by_columns_dropdown=False, clone_pipeline=True, n_sig_figs=3,
        node_scale=12, plotly_params=None
        ):
    """Plot Mapper graphs without interactivity on pipeline parameters.

    The output graph is a rendition of the :class:`igraph.Graph` object
    computed by calling the :meth:`fit_transform` method of the
    :class:`~gtda.mapper.pipeline.MapperPipeline` instance `pipeline` on the
    input `data`. The graph's nodes correspond to subsets of elements (rows) in
    `data`; these subsets are clusters in larger portions of `data` called
    "pullback (cover) sets", which are computed by means of the `pipeline`'s
    "filter function" and "cover" and correspond to the differently-colored
    portions in `this diagram <../../../../_images/mapper_pipeline.svg>`_.
    Two clusters from different pullback cover sets can overlap; if they do, an
    edge between the corresponding nodes in the graph may be drawn.

    Nodes are colored according to `color_variable` and `node_color_statistic`
    and are sized according to the number of elements they represent. The
    hovertext on each node displays, in this order:

        - a globally unique ID for the node, which can be used to retrieve
          node information from the :class:`igraph.Graph` object, see
          :class:`~gtda.mapper.nerve.Nerve`;
        - the label of the pullback (cover) set which the node's elements
          form a cluster in;
        - a label identifying the node as a cluster within that pullback set;
        - the number of elements of `data` associated with the node;
        - the value of the summary statistic which determines the node's color.

    Parameters
    ----------
    pipeline : :class:`~gtda.mapper.pipeline.MapperPipeline` object
        Mapper pipeline to act onto data.

    data : array-like of shape (n_samples, n_features)
        Data used to generate the Mapper graph. Can be a pandas dataframe.

    layout : None, str or callable, optional, default: ``"kamada-kawai"``
        Layout algorithm for the graph. Can be any accepted value for the
        ``layout`` parameter in the :meth:`layout` method of
        :class:`igraph.Graph` [1]_.

    layout_dim : int, default: ``2``
        The number of dimensions for the layout. Can be 2 or 3.

    color_variable : object or None, optional, default: ``None``
        Specifies a feature of interest to be used, together with
        `node_color_statistic`, to determine node colors.

            1. If a numpy array or pandas dataframe, it must have the same
               length as `data`.
            2. ``None`` is equivalent to passing `data`.
            3. If an object implementing :meth:`transform` or
               :meth:`fit_transform`, it is applied to `data` to generate the
               feature of interest.
            4. If an index or string, or list of indices/strings, it is
               equivalent to selecting a column or subset of columns from
               `data`.

    node_color_statistic : None, callable, or ndarray of shape (n_nodes,) or \
        (n_nodes, 1), optional, default: ``None``
        If a callable, node colors will be computed as summary statistics from
        the feature array ``Y`` determined by `color_variable` – specifically,
        the color of a node representing the entries of `data` whose row
        indices are in ``I`` will be ``node_color_statistic(Y[I])``. ``None``
        is equivalent to passing :func:`numpy.mean`. If a numpy array, it must
        have the same length as the number of nodes in the Mapper graph and its
        values are used directly as node colors (`color_variable` is ignored).

    color_by_columns_dropdown : bool, optional, default: ``False``
        If ``True``, a dropdown widget is generated which allows the user to
        color Mapper nodes according to any column in `data` (still using
        `node_color_statistic`) in addition to `color_variable`.

    clone_pipeline : bool, optional, default: ``True``
        If ``True``, the input `pipeline` is cloned before computing the
        Mapper graph to prevent unexpected side effects from in-place
        parameter updates.

    n_sig_figs : int or None, optional, default: ``3``
       If not ``None``, number of significant figures to which to round node
       summary statistics. If ``None``, no rounding is performed.

    node_scale : int or float, optional, default: ``12``
        Sets the scale factor used to determine the rendered size of the
        nodes. Increase for larger nodes. Implements a formula in the
        `Plotly documentation \
        <https://plotly.com/python/bubble-charts/#scaling-the-size-of-bubble\
        -charts>`_.

    plotly_params : dict or None, optional, default: ``None``
        Custom parameters to configure the plotly figure. Allowed keys are
        ``"node_trace"``, ``"edge_trace"`` and ``"layout"``, and the
        corresponding values should be dictionaries containing keyword
        arguments as would be fed to the :meth:`update_traces` and
        :meth:`update_layout` methods of :class:`plotly.graph_objects.Figure`.

    Returns
    -------
    fig : :class:`plotly.graph_objects.Figure` object
        Figure representing the Mapper graph with appropriate node colouring
        and size.

    Examples
    --------
    Setting a colorscale different from the default one:

    >>> import numpy as np
    >>> np.random.seed(1)
    >>> from gtda.mapper import make_mapper_pipeline, plot_static_mapper_graph
    >>> pipeline = make_mapper_pipeline()
    >>> data = np.random.random((100, 3))
    >>> plotly_params = {"node_trace": {"marker_colorscale": "Blues"}}
    >>> fig = plot_static_mapper_graph(pipeline, data,
    ...                                plotly_params=plotly_params)

    Inspect the composition of a node with "Node ID" displayed as 0 in the
    hovertext:

    >>> graph = pipeline.fit_transform(data)
    >>> graph.vs[0]["node_elements"]
    array([70])

    See also
    --------
    plot_interactive_mapper_graph, gtda.mapper.make_mapper_pipeline

    References
    ----------
    .. [1] `igraph.Graph.layout
            <https://igraph.org/python/doc/igraph.Graph-class.html#layout>`_
            documentation.

    """

    # Compute the graph and fetch the indices of points in each node
    _pipeline = clone(pipeline) if clone_pipeline else pipeline

    _node_color_statistic = node_color_statistic or np.mean

    # Simple duck typing to determine whether data is likely a pandas dataframe
    is_data_dataframe = hasattr(data, "columns")

    edge_trace, node_trace, node_elements, node_colors_color_variable = \
        _calculate_graph_data(
            _pipeline, data, is_data_dataframe, layout, layout_dim,
            color_variable, _node_color_statistic, n_sig_figs, node_scale
            )

    # Define layout options
    layout_options = go.Layout(
        **PLOT_OPTIONS_LAYOUT_DEFAULTS["common"],
        **PLOT_OPTIONS_LAYOUT_DEFAULTS[layout_dim]
        )

    fig = go.FigureWidget(data=[edge_trace, node_trace], layout=layout_options)

    _plotly_params = deepcopy(plotly_params)

    # When laying out the graph in 3D, plotly does not automatically give
    # the background hoverlabel the same color as the respective marker,
    # so we do this by hand here.
    # TODO: Extract logic so as to avoid repetitions in interactive version
    colorscale_for_hoverlabel = None
    if layout_dim == 3:
        compute_hoverlabel_bgcolor = True
        if _plotly_params:
            if "node_trace" in _plotly_params:
                if "hoverlabel_bgcolor" in _plotly_params["node_trace"]:
                    fig.update_traces(
                        hoverlabel_bgcolor=_plotly_params["node_trace"].pop(
                            "hoverlabel_bgcolor"
                            ),
                        selector={"name": "node_trace"}
                        )
                    compute_hoverlabel_bgcolor = False
                if "marker_colorscale" in _plotly_params["node_trace"]:
                    fig.update_traces(
                        marker_colorscale=_plotly_params["node_trace"].pop(
                            "marker_colorscale"
                            ),
                        selector={"name": "node_trace"}
                        )

        if compute_hoverlabel_bgcolor:
            colorscale_for_hoverlabel = fig.data[1].marker.colorscale
            node_colors_color_variable = np.asarray(node_colors_color_variable)
            min_col = np.min(node_colors_color_variable)
            max_col = np.max(node_colors_color_variable)
            try:
                hoverlabel_bgcolor = _get_colors_for_vals(
                    node_colors_color_variable, min_col, max_col,
                    colorscale_for_hoverlabel
                    )
            except Exception as e:
                if e.args[0] == "This colorscale is not supported.":
                    warn("Data-dependent background hoverlabel colors cannot "
                         "be generated with this choice of colorscale. Please "
                         "use a standard hex- or RGB-formatted colorscale.",
                         RuntimeWarning)
                else:
                    warn("Something went wrong in generating data-dependent "
                         "background hoverlabel colors. All background "
                         "hoverlabel colors will be set to white.",
                         RuntimeWarning)
                hoverlabel_bgcolor = "white"
                colorscale_for_hoverlabel = None
            fig.update_traces(
                hoverlabel_bgcolor=hoverlabel_bgcolor,
                selector={"name": "node_trace"}
                )

    # Compute node colors according to data columns only if necessary
    if color_by_columns_dropdown:
        hovertext_color_variable = node_trace.hovertext
        column_color_buttons = _get_column_color_buttons(
            data, is_data_dataframe, node_elements, node_colors_color_variable,
            _node_color_statistic, hovertext_color_variable,
            colorscale_for_hoverlabel, n_sig_figs
            )
        # Avoid recomputing hoverlabel bgcolor for top button
        column_color_buttons[0]["args"][0]["hoverlabel.bgcolor"] = \
            [None, fig.data[1].hoverlabel.bgcolor]
    else:
        column_color_buttons = None

    button_height = 1.1
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(buttons=column_color_buttons,
                                 direction="down",
                                 pad={"r": 10, "t": 10},
                                 showactive=True,
                                 x=0.11,
                                 xanchor="left",
                                 y=button_height,
                                 yanchor="top")
            ]
        )

    if color_by_columns_dropdown:
        fig.add_annotation(
            go.layout.Annotation(text="Color by:",
                                 x=0,
                                 xref="paper",
                                 y=button_height - 0.045,
                                 yref="paper",
                                 align="left",
                                 showarrow=False)
            )

    # Update traces and layout according to user input
    if _plotly_params:
        for key in ["node_trace", "edge_trace"]:
            fig.update_traces(
                _plotly_params.pop(key, None),
                selector={"name": key}
                )
        fig.update_layout(_plotly_params.pop("layout", None))

    return fig


def plot_interactive_mapper_graph(
        pipeline, data, layout="kamada_kawai", layout_dim=2,
        color_variable=None, node_color_statistic=None, clone_pipeline=True,
        color_by_columns_dropdown=False, n_sig_figs=3, node_scale=12,
        plotly_params=None
        ):
    """Plot Mapper graphs with interactivity on pipeline parameters.

    Extends :func:`~gtda.mapper.visualization.plot_static_mapper_graph` by
    providing functionality to interactively update parameters from the cover,
    clustering and graph construction steps defined in `pipeline`.

    Parameters
    ----------
    pipeline : :class:`~gtda.mapper.pipeline.MapperPipeline` object
        Mapper pipeline to act on to data.

    data : array-like of shape (n_samples, n_features)
        Data used to generate the Mapper graph. Can be a pandas dataframe.

    layout : None, str or callable, optional, default: ``"kamada-kawai"``
        Layout algorithm for the graph. Can be any accepted value for the
        ``layout`` parameter in the :meth:`layout` method of
        :class:`igraph.Graph` [1]_.

    layout_dim : int, default: ``2``
        The number of dimensions for the layout. Can be 2 or 3.

    color_variable : object or None, optional, default: ``None``
        Specifies a feature of interest to be used, together with
        `node_color_statistic`, to determine node colors.

            1. If a numpy array or pandas dataframe, it must have the same
               length as `data`.
            2. ``None`` is equivalent to passing `data`.
            3. If an object implementing :meth:`transform` or
               :meth:`fit_transform`, it is applied to `data` to generate the
               feature of interest.
            4. If an index or string, or list of indices/strings, it is
               equivalent to selecting a column or subset of columns from
               `data`.

    node_color_statistic : callable or None, optional, default: ``None``
        If a callable, node colors will be computed as summary statistics from
        the feature array ``Y`` determined by `color_variable` – specifically,
        the color of a node representing the entries of `data` whose row
        indices are in ``I`` will be ``node_color_statistic(Y[I])``. ``None``
        is equivalent to passing :func:`numpy.mean`.

    color_by_columns_dropdown : bool, optional, default: ``False``
        If ``True``, a dropdown widget is generated which allows the user to
        color Mapper nodes according to any column in `data` (still using
        `node_color_statistic`) in addition to `color_variable`.

    clone_pipeline : bool, optional, default: ``True``
        If ``True``, the input `pipeline` is cloned before computing the
        Mapper graph to prevent unexpected side effects from in-place
        parameter updates.

    n_sig_figs : int or None, optional, default: ``3``
       If not ``None``, number of significant figures to which to round node
       summary statistics. If ``None``, no rounding is performed.

    node_scale : int or float, optional, default: ``12``
        Sets the scale factor used to determine the rendered size of the
        nodes. Increase for larger nodes. Implements a formula in the
        `Plotly documentation \
        <plotly.com/python/bubble-charts/#scaling-the-size-of-bubble-charts>`_.

    plotly_params : dict or None, optional, default: ``None``
        Custom parameters to configure the plotly figure. Allowed keys are
        ``"node_trace"``, ``"edge_trace"`` and ``"layout"``, and the
        corresponding values should be dictionaries containing keyword
        arguments as would be fed to the :meth:`update_traces` and
        :meth:`update_layout` methods of :class:`plotly.graph_objects.Figure`.

    Returns
    -------
    box : :class:`ipywidgets.VBox` object
        A box containing the following widgets: parameters of the clustering
        algorithm, parameters for the covering scheme, a Mapper graph arising
        from those parameters, a validation box, and logs.

    See also
    --------
    plot_static_mapper_graph, gtda.mapper.pipeline.make_mapper_pipeline

    References
    ----------
    .. [1] `igraph.Graph.layout
            <https://igraph.org/python/doc/igraph.Graph-class.html#layout>`_
            documentation.

    """

    # Clone pipeline to avoid side effects from in-place parameter changes
    _pipeline = clone(pipeline) if clone_pipeline else pipeline

    _node_color_statistic = node_color_statistic or np.mean

    def get_widgets_per_param(params):
        for key, value in params.items():
            style = {'description_width': 'initial'}
            description = key.split("__")[1] if "__" in key else key
            if isinstance(value, float):
                yield (key, widgets.FloatText(
                    value=value,
                    step=0.05,
                    description=description,
                    continuous_update=False,
                    disabled=False,
                    layout=Layout(width="90%"),
                    style=style
                    ))
            elif isinstance(value, bool):
                yield (key, widgets.ToggleButton(
                    value=value,
                    description=description,
                    disabled=False,
                    layout=Layout(width="90%"),
                    style=style
                    ))
            elif isinstance(value, int):
                yield (key, widgets.IntText(
                    value=value,
                    step=1,
                    description=description,
                    continuous_update=False,
                    disabled=False,
                    layout=Layout(width="90%"),
                    style=style
                    ))
            elif isinstance(value, str):
                yield (key, widgets.Text(
                    value=value,
                    description=description,
                    continuous_update=False,
                    disabled=False,
                    layout=Layout(width="90%"),
                    style=style
                    ))

    def on_parameter_change(change):
        handler.clear_logs()
        try:
            for param, value in cover_params.items():
                if isinstance(value, (int, float, str)):
                    _pipeline.set_params(
                        **{param: cover_params_widgets[param].value}
                        )
            for param, value in cluster_params.items():
                if isinstance(value, (int, float, str)):
                    _pipeline.set_params(
                        **{param: cluster_params_widgets[param].value}
                        )
            for param, value in nerve_params.items():
                if isinstance(value, (int, bool)):
                    _pipeline.set_params(
                        **{param: nerve_params_widgets[param].value}
                        )

            logger.info("Updating figure...")
            with fig.batch_update():
                (edge_trace, node_trace, node_elements,
                 node_colors_color_variable) = _calculate_graph_data(
                    _pipeline, data, is_data_dataframe, layout, layout_dim,
                    color_variable, _node_color_statistic, n_sig_figs,
                    node_scale
                    )
                if colorscale_for_hoverlabel is not None:
                    node_colors_color_variable = \
                        np.asarray(node_colors_color_variable)
                    min_col = np.min(node_colors_color_variable)
                    max_col = np.max(node_colors_color_variable)
                    hoverlabel_bgcolor = _get_colors_for_vals(
                        node_colors_color_variable, min_col, max_col,
                        colorscale_for_hoverlabel
                        )
                    fig.update_traces(hoverlabel_bgcolor=hoverlabel_bgcolor,
                                      selector={"name": "node_trace"})

                fig.update_traces(
                    x=node_trace.x,
                    y=node_trace.y,
                    marker_color=node_trace.marker.color,
                    marker_size=node_trace.marker.size,
                    marker_sizeref=node_trace.marker.sizeref,
                    hovertext=node_trace.hovertext,
                    **({"z": node_trace.z} if layout_dim == 3 else dict()),
                    selector={"name": "node_trace"}
                    )
                fig.update_traces(
                    x=edge_trace.x,
                    y=edge_trace.y,
                    **({"z": edge_trace.z} if layout_dim == 3 else dict()),
                    selector={"name": "edge_trace"}
                    )

                # Update color by column buttons
                if color_by_columns_dropdown:
                    hovertext_color_variable = node_trace.hovertext
                    column_color_buttons = _get_column_color_buttons(
                        data, is_data_dataframe, node_elements,
                        node_colors_color_variable, _node_color_statistic,
                        hovertext_color_variable, colorscale_for_hoverlabel,
                        n_sig_figs
                        )
                    # Avoid recomputing hoverlabel bgcolor for top button
                    if colorscale_for_hoverlabel is not None:
                        column_color_buttons[0]["args"][0][
                            "hoverlabel.bgcolor"] = [None, hoverlabel_bgcolor]
                else:
                    column_color_buttons = None

                button_height = 1.1
                fig.update_layout(
                    updatemenus=[
                        go.layout.Updatemenu(
                            buttons=column_color_buttons,
                            direction="down",
                            pad={"r": 10, "t": 10},
                            showactive=True,
                            x=0.11,
                            xanchor="left",
                            y=button_height,
                            yanchor="top"
                            )
                        ])

            valid.value = True
        except Exception:
            exception_data = traceback.format_exc().splitlines()
            logger.exception(exception_data[-1])
            valid.value = False

    def observe_widgets(params, widgets):
        for param, value in params.items():
            if isinstance(value, (int, float, str)):
                widgets[param].observe(on_parameter_change, names="value")

    # Define output widget to capture logs
    out = widgets.Output()

    @out.capture()
    def click_box(change):
        if logs_box.value:
            out.clear_output()
            handler.show_logs()
        else:
            out.clear_output()

    # Initialise logging
    logger = logging.getLogger(__name__)
    handler = OutputWidgetHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Initialise cover, cluster and nerve dictionaries of parameters and
    # widgets
    mapper_params_items = _pipeline.get_mapper_params().items()
    cover_params = {key: value for key, value in mapper_params_items
                    if key.startswith("cover__")}
    cover_params_widgets = dict(get_widgets_per_param(cover_params))
    cluster_params = {key: value for key, value in mapper_params_items
                      if key.startswith("clusterer__")}
    cluster_params_widgets = dict(get_widgets_per_param(cluster_params))
    nerve_params = {key: value for key, value in mapper_params_items
                    if key in ["min_intersection", "contract_nodes"]}
    nerve_params_widgets = dict(get_widgets_per_param(nerve_params))

    # Initialise widgets for validating input parameters of pipeline
    valid = widgets.Valid(
        value=True,
        description="Valid parameters",
        style={"description_width": "100px"},
        )

    # Initialise widget for showing the logs
    logs_box = widgets.Checkbox(
        description="Show logs: ",
        value=False,
        indent=False
        )

    # Initialise figure with initial pipeline and config
    fig = plot_static_mapper_graph(
        _pipeline, data, layout=layout, layout_dim=layout_dim,
        color_variable=color_variable,
        node_color_statistic=_node_color_statistic,
        color_by_columns_dropdown=color_by_columns_dropdown,
        clone_pipeline=False, n_sig_figs=n_sig_figs, node_scale=node_scale,
        plotly_params=plotly_params
        )

    # Store variables for later updates
    is_data_dataframe = hasattr(data, "columns")

    colorscale_for_hoverlabel = None
    if layout_dim == 3:
        # In plot_static_mapper_graph, hoverlabel bgcolors are set to white if
        # something goes wrong in computing them according to the colorscale.
        is_bgcolor_not_white = fig.data[1].hoverlabel.bgcolor != "white"
        user_hoverlabel_bgcolor = False
        if plotly_params:
            if "node_trace" in plotly_params:
                if "hoverlabel_bgcolor" in plotly_params["node_trace"]:
                    user_hoverlabel_bgcolor = True
        if is_bgcolor_not_white and not user_hoverlabel_bgcolor:
            colorscale_for_hoverlabel = fig.data[1].marker.colorscale

    observe_widgets(cover_params, cover_params_widgets)
    observe_widgets(cluster_params, cluster_params_widgets)
    observe_widgets(nerve_params, nerve_params_widgets)

    logs_box.observe(click_box, names="value")

    # Define containers for input widgets
    cover_title = HTML(value="<b>Cover parameters</b>")
    container_cover = widgets.VBox(
        children=[cover_title] + list(cover_params_widgets.values())
        )
    container_cover.layout.align_items = 'center'

    cluster_title = HTML(value="<b>Clusterer parameters</b>")
    container_cluster = widgets.VBox(
        children=[cluster_title] + list(cluster_params_widgets.values()),
        )
    container_cluster.layout.align_items = 'center'

    nerve_title = HTML(value="<b>Nerve parameters</b>")
    container_nerve = widgets.VBox(
        children=[nerve_title] + list(nerve_params_widgets.values()),
        )
    container_nerve.layout.align_items = 'center'

    container_parameters = widgets.HBox(
        children=[container_cover, container_cluster, container_nerve]
        )

    box = widgets.VBox([container_parameters, fig, valid, logs_box, out])
    return box
