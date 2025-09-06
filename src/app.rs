use eframe;
use egui;

use crate::clock::Clock;
use crate::stopwatch::Stopwatch;
use crate::timer::Timer;

#[derive(Default)]
pub struct App {
    clock: Clock,
    stopwatch: Stopwatch,
    timer: Timer,
    current_tab: Tab,
}

#[derive(Default, PartialEq)]
enum Tab {
    #[default]
    Clock,
    Stopwatch,
    Timer,
}

impl eframe::App for App {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.selectable_value(&mut self.current_tab, Tab::Clock, "Clock");
                ui.selectable_value(&mut self.current_tab, Tab::Stopwatch, "Stopwatch");
                ui.selectable_value(&mut self.current_tab, Tab::Timer, "Timer");
            });
            
            ui.separator();
            
            match self.current_tab {
                Tab::Clock => self.clock.ui(ui),
                Tab::Stopwatch => self.stopwatch.ui(ui),
                Tab::Timer => self.timer.ui(ui),
            }
        });
    }
}