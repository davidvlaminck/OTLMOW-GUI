// Handle the right clic rectangle selection of nodes
// ========
//most of this code with slight adjustments is from github user: Vincent-CIRCL

// https://github.com/almende/vis/issues/3594

const NO_CLICK = 0;
const RIGHT_CLICK = 3;

// Selector
function canvasify(DOMx, DOMy) {
    const { x, y } = network.DOMtoCanvas({ x: DOMx, y: DOMy });
    return [x, y];
}

function correctRange(start, end){
    return start < end ? [start, end] : [end, start];
}

function selectFromDOMRect(){
    const [sX, sY] = canvasify(DOMRect.startX, DOMRect.startY);
    const [eX, eY] = canvasify(DOMRect.endX, DOMRect.endY);
    const [startX, endX] = correctRange(sX, eX);
    const [startY, endY] = correctRange(sY, eY);

    nodeList = []
    for (const nodeId of network.body.data.nodes._data.keys())
    {
        const { x, y } = network.getPosition(nodeId);
        if (startX <= x && x <= endX && startY <= y && y <= endY)
            nodeList.push(nodeId)
    }
    ctrlSelectedNodesList = nodeList
    network.selectNodes(ctrlSelectedNodesList);

}

function rectangle_mousedown(evt){
    // Handle mouse down event = beginning of the rectangle selection

    var pageX = event.pageX;    // Get the horizontal coordinate
    var pageY = event.pageY;    // Get the vertical coordinate
    var which = event.which;    // Get the button type

    // When mousedown, save the initial rectangle state
    if(which === RIGHT_CLICK) {
        Object.assign(DOMRect, {
            startX: pageX - container.offsetLeft,
            startY: pageY - container.offsetTop,
            endX: pageX - container.offsetLeft,
            endY: pageY - container.offsetTop
        });
        drag = true;

        node_id_when_last_right_click_down = currentlyHoveredNode;
    }
}

function rectangle_mousedrag(evt){
    // Handle mouse drag event = during the rectangle selection
    var pageX = event.pageX;    // Get the horizontal coordinate
    var pageY = event.pageY;    // Get the vertical coordinate
    var which = event.which;    // Get the button type

    if(which === NO_CLICK && drag) {
        // Make selection rectangle disappear when accidently mouseupped outside 'container'
        drag = false;
        network.redraw();
    } else if(drag) {
        drag_happened = true
        // When mousemove, update the rectangle state
        Object.assign(DOMRect, {
            endX: pageX - container.offsetLeft,
            endY: pageY - container.offsetTop
        });
        network.redraw();
    }

}

function rectangle_mouseup(evt){
    // Handle mouse up event = beginning of the rectangle selection

    var pageX = event.pageX;    // Get the horizontal coordinate
    var pageY = event.pageY;    // Get the vertical coordinate
    var which = event.which;    // Get the button type

    // When mouseup, select the nodes in the rectangle
    if(which === RIGHT_CLICK) {
        if(drag && drag_happened)
        {
            //if the user dragged then a rectangle was drawn and elements need to be selected
            network.redraw();
            selectFromDOMRect();
            drag_happened = false
        }
        else
        {
            node_id_at_mouse_up = currentlyHoveredNode;
            if( node_id_at_mouse_up &&
                node_id_when_last_right_click_down  == node_id_at_mouse_up &&
                node_id_at_mouse_up.includes('edgeJoint'))
            {
                removeEdgeJointNode(node_id_at_mouse_up)
            }
        }
        node_id_when_last_right_click_down = null;
        drag = false;


    }

}

function draw_rectangle_on_network(ctx){
    // Draw a rectangle regarding the current selection
    if(drag) {
        const [startX, startY] = canvasify(DOMRect.startX, DOMRect.startY);
        const [endX, endY] = canvasify(DOMRect.endX, DOMRect.endY);

        ctx.setLineDash([5]);
        ctx.strokeStyle = 'rgba(78, 146, 237, 0.75)';
        ctx.strokeRect(startX, startY, endX - startX, endY - startY);
        ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(151, 194, 252, 0.45)';
        ctx.fillRect(startX, startY, endX - startX, endY - startY);
    }
}


function makeMeMultiSelect(container, network) {
    // State
    node_id_when_last_right_click_down = null;
    drag = false;
    drag_happened = false;
    DOMRect = {};

    // Disable default right-click dropdown menu
    container.oncontextmenu = () => false;

    // Listeners
    //container.mousedown()
    document.addEventListener("mousedown", function(evt) { rectangle_mousedown(evt) });
    document.addEventListener("mousemove", function(evt) { rectangle_mousedrag(evt) });
    document.addEventListener("mouseup", function(evt) { rectangle_mouseup(evt) });

    // Drawer
    network.on('afterDrawing', function (ctx) { draw_rectangle_on_network(ctx) });
}