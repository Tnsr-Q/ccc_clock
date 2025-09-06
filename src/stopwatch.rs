use egui;

#[derive(Default)]
pub struct Stopwatch {
    elapsed_time: f64,
    is_running: bool,
}

impl Stopwatch {
    pub fn ui(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.heading("Stopwatch");
            ui.separator();
            
            // Display time
            let minutes = (self.elapsed_time / 60.0) as u32;
            let seconds = (self.elapsed_time % 60.0) as u32;
            let centiseconds = ((self.elapsed_time % 1.0) * 100.0) as u32;
            
            ui.allocate_ui(egui::vec2(300.0, 80.0), |ui| {
                ui.centered_and_justified(|ui| {
                    ui.label(
                        egui::RichText::new(format!("{:02}:{:02}.{:02}", minutes, seconds, centiseconds))
                            .size(48.0)
                            .strong()
                    );
                });
            });
            
            ui.add_space(20.0);
            
            // Controls
            ui.horizontal(|ui| {
                if self.is_running {
                    if ui.button("Stop").clicked() {
                        self.is_running = false;
                    }
                } else {
                    if ui.button("Start").clicked() {
                        self.is_running = true;
                    }
                }
                
                if ui.button("Reset").clicked() {
                    self.elapsed_time = 0.0;
                    self.is_running = false;
                }
            });
            
            // Update elapsed time
            if self.is_running {
                self.elapsed_time += ui.input(|i| i.unstable_dt) as f64;
            }
        });
    }
}