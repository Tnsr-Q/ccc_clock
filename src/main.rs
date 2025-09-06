pub mod app;
pub mod clock;
pub mod stopwatch;
pub mod timer;
pub mod utils;

use app::App;
use eframe::egui;

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([400.0, 300.0]),
        ..Default::default()
    };
    
    eframe::run_native(
        "CCC Clock",
        options,
        Box::new(|_cc| Box::new(App::default())),
    )
}