use chrono;
use egui;

#[derive(Default)]
pub struct Clock {}

impl Clock {
    pub fn ui(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.heading("Current Time");
            ui.separator();
            
            let now = chrono::Local::now();
            ui.label(format!("Date: {}", now.format("%Y-%m-%d")));
            ui.label(format!("Time: {}", now.format("%H:%M:%S")));
            ui.label(format!("Day: {}", now.format("%A")));
            
            ui.add_space(20.0);
            
            // Add a large time display
            ui.allocate_ui(egui::vec2(300.0, 80.0), |ui| {
                ui.centered_and_justified(|ui| {
                    ui.label(
                        egui::RichText::new(now.format("%H:%M:%S").to_string())
                            .size(48.0)
                            .strong()
                    );
                });
            });
        });
    }
}