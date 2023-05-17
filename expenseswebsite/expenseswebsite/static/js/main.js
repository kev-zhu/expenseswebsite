// addition of try/catch block bc if none expense input, then querySelector would not find any with that id

try {
    deleteBtns = document.querySelectorAll('#confirm-delete')

    deleteBtns.forEach(deleteBtn => {
        deleteBtn.onclick = () => {
            return confirm('Are you sure you want to delete this expense?')
        }
    })
} catch (error) {
}

// onclick works as a property -- and property needs to be returned as true/false to continue/cancel deletion
// deleteBtn.addEventListener('click', () => {
//     return confirm('Are you sure you want to delete this expense?')
// })
