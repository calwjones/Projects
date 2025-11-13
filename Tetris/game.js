const canvas = document.getElementById('game-board'); // from index.html
const context = canvas.getContext('2d');

const COLS = 10; // usual tetris width
const ROWS = 20; // usual tetris height
const BLOCK_SIZE = 30;

canvas.width = COLS * BLOCK_SIZE;
canvas.height = ROWS * BLOCK_SIZE;
context.scale(BLOCK_SIZE, BLOCK_SIZE);

context.fillStyle = 'black';
context.fillRect(0, 0, canvas.width, canvas.height);

let board = []; // 2d array for the grid
for (let row = 0; row < ROWS; row++) {
    let newRow = [];
    for (let col = 0; col < COLS; col++) {
        newRow.push(0);
    }
    board.push(newRow);
}

const PIECES = { // shaping the 7 tetris pieces
    T: [
        [0, 1, 0],
        [1, 1, 1]
    ],
    O: [
        [2, 2],
        [2, 2]
    ],
    L: [
        [0, 0, 3],
        [3, 3, 3]
    ],
    J: [
        [4, 0, 0],
        [4, 4, 4]
    ],
    I: [
        [5, 5, 5, 5]
    ],
    S: [
        [0, 6, 6],
        [6, 6, 0]
    ],
    Z: [
        [7, 7, 0],
        [0, 7, 7]
    ]
};

const COLORS = [
    null,
    '#9B59B6', // T - Purple
    '#F1C40F', // O - Yellow
    '#E67E22', // L - Orange
    '#3498DB', // J - Blue
    '#1ABC9C', // I - Teal
    '#2ECC71', // S - Green
    '#E74C3C'  // Z - Red
];


let player = {
    pos: { x: 3, y: 0 }, // top middle of grid
    matrix: PIECES.T
};

function draw() {
    // loop through each row of the pieces matrix
    player.matrix.forEach((row, y) => {
        // loop through each cell in that row
        row.forEach((value, x) => {
            // if not 0, need to draw
            if (value !== 0) {
                // set colour based on the value
                context.fillStyle = COLORS[value];
                context.fillRect(
                    player.pos.x + x, // the piece x pos + the block x pos
                    player.pos.y + y, // the piece y pos + the block y pos
                    1, 1 // 1x1 block
                );
            }
        });
    });
}

draw()