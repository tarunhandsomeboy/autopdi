import os
import sys
from datetime import datetime, date, time, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.showroom import Showroom
from models.inspector import Inspector, InspectorSpecialization, InspectorAvailability
from models.equipment import Equipment
from models.certification import Certification
from models.booking import Booking
from models.inspection import Inspection, InspectionCategory
from models.checkpoint import InspectionCheckpoint
from models.media import InspectionMedia
from models.ai_finding import AIFinding
from models.report import Report
from models.rating import Rating
from models.notification import Notification
from models.issue import IssueResolution
from routes.inspection_routes import generate_checkpoints_for_inspection
from services.report_service import generate_pdf_report
from services.notification_service import create_notification


def generate_sample_images(base_dir: Path):
    """Generates realistic vehicle component placeholder inspection images."""
    insp_dir = base_dir / 'uploads' / 'inspections'
    os.makedirs(insp_dir, exist_ok=True)

    samples = [
        ("front_bumper_scratch.jpg", "Front Bumper - Surface Scratch Detected", (230, 240, 255), (37, 99, 235)),
        ("door_panel_dent.jpg", "Right Rear Door - Sheet Metal Pressure Dent", (255, 245, 230), (217, 119, 6)),
        ("paint_thickness_gauge.jpg", "Paint Gauge Reading - 118 Microns (Nominal)", (235, 255, 240), (16, 185, 129)),
        ("ev_battery_casing.jpg", "Underbody High-Voltage Battery Shield - Pristine", (245, 240, 255), (124, 58, 237)),
        ("tire_tread_depth.jpg", "Tire Tread Depth Digital Gauge - 7.8mm", (240, 245, 250), (15, 23, 42))
    ]

    for fname, label, bg_color, text_color in samples:
        fpath = insp_dir / fname
        if not fpath.exists():
            img = Image.new('RGB', (800, 500), color=bg_color)
            draw = ImageDraw.Draw(img)
            # Draw aesthetic border and label
            draw.rectangle([(20, 20), (780, 480)], outline=text_color, width=3)
            draw.text((40, 50), "AUTO PDI — EVIDENCE CAPTURE", fill=text_color)
            draw.text((40, 90), f"TIMESTAMP: {datetime.utcnow().strftime('%d %b %Y, %I:%M %p')}", fill=(100, 116, 139))
            draw.text((40, 130), f"GPS: 12.9716° N, 77.5946° E (Bangalore Showroom)", fill=(100, 116, 139))
            draw.text((40, 240), label, fill=text_color)
            img.save(str(fpath), quality=90)


def seed_database():
    app = create_app('development')
    with app.app_context():
        print("[SEED] Initializing database schema...")
        db.create_all()

        # Check if already seeded
        if User.query.filter_by(email='admin@autopdi.com').first():
            print("[SEED] Database already contains seed records. Re-seeding clean state...")
            db.drop_all()
            db.create_all()

        base_dir = Path(app.config['UPLOAD_FOLDER']).parent
        generate_sample_images(base_dir)

        print("[SEED] Seeding Users & Admins...")
        
        # 1. Admin
        admin = User(
            name="PDI Lead Administrator",
            email="admin@autopdi.com",
            phone="+91 98765 43210",
            role="ADMIN",
            status="ACTIVE"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

        # 2. Customer
        customer = User(
            name="Karthik Menon",
            email="customer@autopdi.com",
            phone="+91 98450 11223",
            role="CUSTOMER",
            status="ACTIVE"
        )
        customer.set_password("Customer@123")
        db.session.add(customer)

        # Additional Customer
        customer2 = User(
            name="Sneha Rao",
            email="sneha@autopdi.com",
            phone="+91 97312 88990",
            role="CUSTOMER",
            status="ACTIVE"
        )
        customer2.set_password("Customer@123")
        db.session.add(customer2)

        # 3. 5 Professional Inspectors
        inspectors_data = [
            {
                "name": "Arun Kumar",
                "email": "inspector@autopdi.com",
                "phone": "+91 98860 55443",
                "password": "Inspector@123",
                "bio": "Senior Automotive Diagnostic Master with 8+ years specializing in paint thickness inspection, powertrain analysis, and EV diagnostics.",
                "experience_years": 8,
                "total_inspections": 1240,
                "rating": 4.9,
                "trust_score": 96,
                "verification_status": "VERIFIED",
                "availability_status": "AVAILABLE",
                "lat": 12.9716,
                "lon": 77.5946,
                "specialization": "ICE, EV, Hybrid - Hyundai, Tata, Kia, Mahindra",
                "price_std": 1499.00,
                "price_prem": 2499.00,
                "equipment": [
                    ("Paint Thickness Gauge (Dual F/NF)", "SENSOR", "PTG-9982X"),
                    ("OBD-II Multi-Brand Scanner", "DIAGNOSTIC", "OBD-LAUNCH-V4"),
                    ("Digital Tire Tread Depth Gauge", "SENSOR", "TDG-881"),
                    ("12V & EV Battery Impedance Tester", "ELECTRICAL", "BAT-TEST-PRO"),
                    ("Thermal Imaging Infrared Camera", "OPTICAL", "FLIR-E4-PRO")
                ],
                "certs": [
                    ("Certified Master Vehicle Inspector (CMVI)", "ASE Automotive", "ASE-INSP-8821"),
                    ("High Voltage EV Safety & Diagnostics L3", "SAE International", "SAE-EV-4412")
                ]
            },
            {
                "name": "Rahul Sharma",
                "email": "rahul.pdi@autopdi.com",
                "phone": "+91 98112 33445",
                "password": "Inspector@123",
                "bio": "Certified Body & Frame Specialist with 6 years experience in sheet metal alignment, clear-coat analysis, and road test quality.",
                "experience_years": 6,
                "total_inspections": 840,
                "rating": 4.7,
                "trust_score": 91,
                "verification_status": "VERIFIED",
                "availability_status": "AVAILABLE",
                "lat": 12.9352,
                "lon": 77.6245,
                "specialization": "ICE, Hybrid - Toyota, Honda, Maruti Suzuki",
                "price_std": 1399.00,
                "price_prem": 2299.00,
                "equipment": [
                    ("Digital Paint Depth Meter", "SENSOR", "PDM-550"),
                    ("OBD-II Bluetooth Scanner", "DIAGNOSTIC", "OBD-SCAN-22"),
                    ("Brake Fluid Moisture Tester", "ELECTRICAL", "BFT-101")
                ],
                "certs": [
                    ("Automotive Body & Paint QA Inspector", "ARA India", "ARA-QA-509")
                ]
            },
            {
                "name": "Priya Auto Expert",
                "email": "priya.pdi@autopdi.com",
                "phone": "+91 99001 77665",
                "password": "Inspector@123",
                "bio": "Chief EV & Connected Vehicle Specialist with 10 years experience. Conducted 1800+ inspections across Luxury & EV segments.",
                "experience_years": 10,
                "total_inspections": 1800,
                "rating": 4.9,
                "trust_score": 98,
                "verification_status": "VERIFIED",
                "availability_status": "AVAILABLE",
                "lat": 12.9850,
                "lon": 77.7200,
                "specialization": "EV, Hybrid, Luxury ICE - Tata EV, MG, BYD, BMW",
                "price_std": 1699.00,
                "price_prem": 2799.00,
                "equipment": [
                    ("EV Traction Battery Diagnostic Unit", "DIAGNOSTIC", "EV-BMS-SCAN-X"),
                    ("Paint Thickness Gauge", "SENSOR", "PTG-ACCU-7"),
                    ("Thermal Leak & Insulation Detector", "OPTICAL", "THERM-889")
                ],
                "certs": [
                    ("Electric Vehicle Systems Expert", "TÜV SÜD", "TUV-EV-9021"),
                    ("Advanced Vehicle Safety Auditor", "SAE India", "SAE-AUD-1002")
                ]
            },
            {
                "name": "Vikram Singh",
                "email": "vikram.pdi@autopdi.com",
                "phone": "+91 97400 33221",
                "password": "Inspector@123",
                "bio": "Powertrain & 4x4 Offroad Specialist with 5 years experience inspecting heavy SUVs, suspensions, and underbody mechanics.",
                "experience_years": 5,
                "total_inspections": 620,
                "rating": 4.8,
                "trust_score": 89,
                "verification_status": "VERIFIED",
                "availability_status": "AVAILABLE",
                "lat": 12.9279,
                "lon": 77.6271,
                "specialization": "ICE 4x4, Diesel - Mahindra, Tata, Force, Toyota",
                "price_std": 1499.00,
                "price_prem": 2399.00,
                "equipment": [
                    ("Underbody Scope & Endoscope Camera", "OPTICAL", "ENDO-CAM-4K"),
                    ("OBD-II Diesel Diagnostic Tool", "DIAGNOSTIC", "DSL-DIAG-9")
                ],
                "certs": [
                    ("Certified Powertrain Specialist", "National Institute of Tech", "NIT-PT-771")
                ]
            },
            {
                "name": "Ananya Sen",
                "email": "ananya.pdi@autopdi.com",
                "phone": "+91 96112 44556",
                "password": "Inspector@123",
                "bio": "Automotive Electronics & Infotainment specialist with 3 years experience. Focus on ADAS, sensors, and interior QA.",
                "experience_years": 3,
                "total_inspections": 290,
                "rating": 4.6,
                "trust_score": 84,
                "verification_status": "PENDING",  # Great for demonstrating Admin approval flow!
                "availability_status": "AVAILABLE",
                "lat": 13.0358,
                "lon": 77.5970,
                "specialization": "ICE, EV - Kia, Hyundai, Skoda",
                "price_std": 1299.00,
                "price_prem": 2099.00,
                "equipment": [
                    ("ADAS Calibration Target & Meter", "OPTICAL", "ADAS-TGT-2")
                ],
                "certs": [
                    ("Automotive Embedded Electronics Certificate", "IETE", "IETE-EMB-334")
                ]
            }
        ]

        inspector_objs = []
        for idata in inspectors_data:
            u = User(
                name=idata["name"],
                email=idata["email"],
                phone=idata["phone"],
                role="INSPECTOR",
                status="ACTIVE" if idata["verification_status"] == "VERIFIED" else "PENDING"
            )
            u.set_password(idata["password"])
            db.session.add(u)
            db.session.flush()

            insp = Inspector(
                user_id=u.id,
                bio=idata["bio"],
                experience_years=idata["experience_years"],
                total_inspections=idata["total_inspections"],
                rating=idata["rating"],
                trust_score=idata["trust_score"],
                verification_status=idata["verification_status"],
                availability_status=idata["availability_status"],
                latitude=idata["lat"],
                longitude=idata["lon"],
                specialization=idata["specialization"],
                price_standard=idata["price_std"],
                price_premium=idata["price_prem"]
            )
            db.session.add(insp)
            db.session.flush()
            inspector_objs.append(insp)

            # Add equipment
            for eq_name, eq_type, snum in idata["equipment"]:
                eq = Equipment(
                    inspector_id=insp.id,
                    equipment_name=eq_name,
                    equipment_type=eq_type,
                    serial_number=snum,
                    verification_status="VERIFIED" if idata["verification_status"] == "VERIFIED" else "PENDING"
                )
                db.session.add(eq)

            # Add certifications
            for c_name, issuer, c_num in idata["certs"]:
                cert = Certification(
                    inspector_id=insp.id,
                    certificate_name=c_name,
                    issuer=issuer,
                    certificate_number=c_num,
                    issue_date=date(2023, 1, 15),
                    expiry_date=date(2028, 1, 15),
                    verification_status="VERIFIED" if idata["verification_status"] == "VERIFIED" else "PENDING"
                )
                db.session.add(cert)

        print("[SEED] Seeding Showrooms...")
        showrooms_data = [
            ("ABC Hyundai Flagship", "100 Feet Road, Indiranagar", "Bangalore", "Karnataka", "560038", "+91 80 2521 9900", 12.9784, 77.6408),
            ("Tata Motors EV Hub", "ITPL Main Road, Whitefield", "Bangalore", "Karnataka", "560066", "+91 80 4112 8800", 12.9850, 77.7300),
            ("Mahindra Automall", "80 Feet Road, Koramangala", "Bangalore", "Karnataka", "560034", "+91 80 2553 4400", 12.9352, 77.6245),
            ("Kia Motors City Center", "Hosur Road, Electronic City", "Bangalore", "Karnataka", "560100", "+91 80 6718 2200", 12.8450, 77.6600),
            ("Toyota Prime", "MG Road, Central Business District", "Bangalore", "Karnataka", "560001", "+91 80 2558 1100", 12.9750, 77.6050)
        ]

        showroom_objs = []
        for name, addr, city, st, pin, contact_num, lat, lon in showrooms_data:
            s = Showroom(
                name=name,
                address=addr,
                city=city,
                state=st,
                postal_code=pin,
                contact_number=contact_num,
                latitude=lat,
                longitude=lon
            )
            db.session.add(s)
            db.session.flush()
            showroom_objs.append(s)

        print("[SEED] Seeding Customer Vehicles...")
        vehicles_data = [
            (customer.id, "Hyundai", "Creta", "SX(O) 1.5 Turbo DCT", "Petrol", "ICE", "DEMOVIN123456", "KA03MJ2026", date(2026, 7, 10)),
            (customer.id, "Tata", "Nexon EV", "Fearless+ Long Range 45kWh", "Electric", "EV", "NEXONEV2026X9", "KA05EV8821", date(2026, 6, 20)),
            (customer.id, "Mahindra", "Thar Roxx", "AX7L 4x4 Diesel AT", "Diesel", "ICE", "THAR4X4ROXX01", "KA01TH9900", date(2026, 5, 14)),
            (customer2.id, "Kia", "Seltos", "GTX+ 1.5 TGDi", "Petrol", "ICE", "SELTOSGTX2026", "KA04SL4455", date(2026, 7, 1)),
            (customer2.id, "Toyota", "Innova Hycross", "ZX(O) Strong Hybrid 2.0L", "Hybrid", "HYBRID", "HYCROSSHYB2026", "KA02HY7711", date(2026, 4, 18))
        ]

        vehicle_objs = []
        for cid, brand, model, var, fuel, vtype, vin, reg, mfg in vehicles_data:
            v = Vehicle(
                customer_id=cid,
                brand=brand,
                model=model,
                variant=var,
                fuel_type=fuel,
                vehicle_type=vtype,
                vin=vin,
                registration_number=reg,
                manufacturing_date=mfg
            )
            db.session.add(v)
            db.session.flush()
            vehicle_objs.append(v)

        db.session.commit()

        print("[SEED] Seeding Complete Demo Scenario: Completed Inspection + Report + Issues...")
        # 1. Completed Inspection for Customer 1 (Hyundai Creta)
        arun_inspector = inspector_objs[0]
        creta_vehicle = vehicle_objs[0]
        hyundai_showroom = showroom_objs[0]

        booking_completed = Booking(
            customer_id=customer.id,
            vehicle_id=creta_vehicle.id,
            showroom_id=hyundai_showroom.id,
            inspector_id=arun_inspector.id,
            inspection_type="PREMIUM",
            scheduled_date=date.today() - timedelta(days=2),
            scheduled_time=time(10, 30),
            price=2499.00,
            status="COMPLETED",
            payment_status="PAID",
            notes="Please double check paint thickness on right doors and bumper alignment."
        )
        db.session.add(booking_completed)
        db.session.flush()

        inspection_completed = Inspection(
            booking_id=booking_completed.id,
            vehicle_id=creta_vehicle.id,
            inspector_id=arun_inspector.id,
            vin_verified=True,
            started_at=datetime.utcnow() - timedelta(days=2, hours=3),
            completed_at=datetime.utcnow() - timedelta(days=2, hours=1),
            overall_score=88.0,
            final_status="ATTENTION_REQUIRED",
            ai_score=91.0,
            verification_code="PDI-2026-X8Y9Z"
        )
        db.session.add(inspection_completed)
        db.session.flush()

        # Checkpoints for completed inspection
        generate_checkpoints_for_inspection(inspection_completed)

        # Flag 2 items as ATTENTION / FAIL to simulate real automotive PDI
        cp_scratch = InspectionCheckpoint.query.filter_by(
            inspection_id=inspection_completed.id,
            item_name="Clear-Coat Scratch & Swirl Mark Assessment"
        ).first()

        if cp_scratch:
            cp_scratch.status = "ATTENTION"
            cp_scratch.severity = "LOW"
            cp_scratch.remark = "AI Detected: Possible scratch on front bumper corner. Clear-coat rub needed."
            cp_scratch.ai_detected = True
            cp_scratch.ai_confidence = 0.91

            # Add media & AI finding
            media1 = InspectionMedia(
                inspection_id=inspection_completed.id,
                checkpoint_id=cp_scratch.id,
                file_url="/uploads/inspections/front_bumper_scratch.jpg",
                file_type="IMAGE",
                latitude=12.9784,
                longitude=77.6408,
                captured_at=datetime.utcnow() - timedelta(days=2, hours=2),
                ai_analysis="Clear-coat surface scratch detected on Front Bumper. Length ~4.2cm.",
                ai_confidence=0.91
            )
            db.session.add(media1)
            db.session.flush()

            ai_finding1 = AIFinding(
                inspection_id=inspection_completed.id,
                checkpoint_id=cp_scratch.id,
                image_id=media1.id,
                finding_type="Possible Scratch",
                description="Clear-coat surface scratch detected on front bumper corner. Length ~4.2cm.",
                confidence=0.91,
                severity="LOW",
                inspector_confirmation="CONFIRMED"
            )
            db.session.add(ai_finding1)

            # Create Dealer Issue
            issue1 = IssueResolution(
                inspection_id=inspection_completed.id,
                checkpoint_id=cp_scratch.id,
                issue_description="Front bumper right corner clear-coat surface scratch (4.2cm). Requires 3M compound polishing.",
                status="DEALER_NOTIFIED",
                dealer_response="Dealer body shop notified. Scheduled for pre-delivery detailing."
            )
            db.session.add(issue1)

        # Generate official PDF Report
        doc_folder = Path(app.config['DOCUMENTS_UPLOAD_FOLDER'])
        generate_pdf_report(inspection_completed, doc_folder)

        # Add Customer Rating for this completed inspection
        rating1 = Rating(
            booking_id=booking_completed.id,
            customer_id=customer.id,
            inspector_id=arun_inspector.id,
            rating=5.0,
            review="Incredible thoroughness! Arun caught a bumper clear-coat scratch and got the dealer to buff it out before delivery."
        )
        db.session.add(rating1)

        # 2. In-Progress Inspection (Tata Nexon EV)
        booking_in_prog = Booking(
            customer_id=customer.id,
            vehicle_id=vehicle_objs[1].id,
            showroom_id=showroom_objs[1].id,
            inspector_id=arun_inspector.id,
            inspection_type="PREMIUM",
            scheduled_date=date.today(),
            scheduled_time=time(11, 0),
            price=2499.00,
            status="IN_PROGRESS",
            payment_status="PAID"
        )
        db.session.add(booking_in_prog)
        db.session.flush()

        insp_in_prog = Inspection(
            booking_id=booking_in_prog.id,
            vehicle_id=vehicle_objs[1].id,
            inspector_id=arun_inspector.id,
            vin_verified=True,
            started_at=datetime.utcnow() - timedelta(minutes=45),
            overall_score=94.5,
            final_status="DELIVERY_READY",
            verification_code="PDI-2026-EV99A"
        )
        db.session.add(insp_in_prog)
        db.session.flush()
        generate_checkpoints_for_inspection(insp_in_prog)

        # 3. Pending/Requested Booking (Mahindra Thar)
        booking_req = Booking(
            customer_id=customer.id,
            vehicle_id=vehicle_objs[2].id,
            showroom_id=showroom_objs[2].id,
            inspector_id=arun_inspector.id,
            inspection_type="PREMIUM",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time=time(14, 0),
            price=2499.00,
            status="REQUESTED",
            payment_status="PAID",
            notes="Please inspect underbody 4x4 transfer case and roof hardtop seals."
        )
        db.session.add(booking_req)

        # 4. Additional historic bookings for charts
        for i in range(1, 6):
            hist_booking = Booking(
                customer_id=customer2.id,
                vehicle_id=vehicle_objs[3].id if i % 2 == 0 else vehicle_objs[4].id,
                showroom_id=showroom_objs[i % len(showroom_objs)].id,
                inspector_id=inspector_objs[i % len(inspector_objs)].id,
                inspection_type="PREMIUM" if i % 2 == 0 else "STANDARD",
                scheduled_date=date.today() - timedelta(days=i * 12),
                scheduled_time=time(10 + i, 0),
                price=2499.00 if i % 2 == 0 else 1499.00,
                status="COMPLETED",
                payment_status="PAID"
            )
            db.session.add(hist_booking)

        # 5. Welcome notifications
        create_notification(
            user_id=customer.id,
            booking_id=booking_completed.id,
            title="PDI Report Ready: Hyundai Creta",
            message="Your pre-delivery inspection report PDI-2026-X8Y9Z is ready for download.",
            notif_type="SUCCESS"
        )

        db.session.commit()
        print("[SUCCESS] Auto PDI Database seeded successfully with realistic automotive test data!")


if __name__ == '__main__':
    seed_database()
