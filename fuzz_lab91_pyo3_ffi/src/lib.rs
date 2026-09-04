use pyo3::prelude::*;

/// Safe function: returns a string owned by Rust, copied to Python.
#[pyfunction]
fn get_string_safe(input: &str) -> PyResult<String> {
    Ok(format!("Hello, {}!", input))
}

/// Buggy function: returns a string that references freed memory.
/// This creates a dangling pointer using unsafe to simulate a use-after-free.
#[pyfunction]
fn get_string_buggy(input: &str) -> PyResult<String> {
    // Allocate a Vec and fill it
    let mut bytes = Vec::new();
    bytes.extend_from_slice(b"Hello, ");
    bytes.extend_from_slice(input.as_bytes());
    bytes.push(b'!');

    // BUG: create a String from the Vec's raw parts, but then drop the Vec.
    // This leaves the String pointing to freed memory.
    let ptr = bytes.as_ptr();
    let len = bytes.len();
    let cap = bytes.capacity();
    // Forget the Vec to avoid double-free
    std::mem::forget(bytes);
    // Now create a String from the raw pointer (which is now a dangling pointer)
    // This is undefined behavior and will crash when the string is accessed.
    let dangling = unsafe { String::from_raw_parts(ptr as *mut u8, len, cap) };
    Ok(dangling)
}

/// Module definition
#[pymodule]
fn pyo3_ffi_target(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_string_safe, m)?)?;
    m.add_function(wrap_pyfunction!(get_string_buggy, m)?)?;
    Ok(())
}
