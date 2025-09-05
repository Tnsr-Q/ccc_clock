use egui;

#[derive(Default)]
pub struct Timer {
    target_minutes: u32,
    target_seconds: u32,
    remaining_time: f64,
    is_running: bool,
    is_finished: bool,
}

impl Timer {
    pub fn ui(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.heading("Timer");
            ui.separator();
            
            // Timer setup
            if !self.is_running {
                ui.horizontal(|ui| {
                    ui.label("Minutes:");
                    ui.add(egui::DragValue::new(&mut self.target_minutes).clamp_range(0..=59));
                    ui.label("Seconds:");
                    ui.add(egui::DragValue::new(&mut self.target_seconds).clamp_range(0..=59));
                });
                
                if ui.button("Start Timer").clicked() {
                    self.remaining_time = (self.target_minutes * 60 + self.target_seconds) as f64;
                    self.is_running = true;
                    self.is_finished = false;
                }
            }
            
            // Timer display
            let minutes = (self.remaining_time / 60.0) as u32;
            let seconds = (self.remaining_time % 60.0) as u32;
            
            ui.allocate_ui(egui::vec2(300.0, 80.0), |ui| {
                ui.centered_and_justified(|ui| {
                    let color = if self.is_finished {
                        egui::Color32::RED
                    } else {
                        egui::Color32::from_rgb(255, 255, 255)
                    };
                    
                    ui.label(
                        egui::RichText::new(format!("{:02}:{:02}", minutes, seconds))
                            .size(48.0)
                            .strong()
                            .color(color)
                    );
                });
            });
            
            // Timer controls
            if self.is_running {
                if ui.button("Stop Timer").clicked() {
                    self.is_running = false;
                    self.is_finished = false;
                }
                
                // Update timer
                if self.remaining_time > 0.0 {
                    self.remaining_time -= ui.input(|i| i.unstable_dt) as f64;
                } else {
                    self.remaining_time = 0.0;
                    self.is_finished = true;
                }
            }
            
            if self.is_finished {
                ui.label(egui::RichText::new("⏰ Time's up!").size(24.0).strong());
            }
        });
    }
}