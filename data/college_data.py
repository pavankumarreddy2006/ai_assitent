# =====================================================
# data.py - COMPLETE COLLEGE DATA ARCHITECTURE
# =====================================================
# Exact Architecture as per your requirement
# Last Updated: April 2026
# =====================================================

# =====================================================
# COLLEGE BASIC INFORMATION (DEFINED FIRST)
# =====================================================
COLLEGE_NAME = "Ideal College of Arts and Sciences"
COLLEGE_PHONE = "0884-2384382 / 0884-2384381"
COLLEGE_EMAIL = "idealcolleges@gmail.com"
COLLEGE_WEBSITE = "https://idealcollege.edu.in"
COLLEGE_LOCATION = "Vidyuth Nagar, Kakinada, Andhra Pradesh"

COLLEGE_KEYWORDS = [
    "college", "admissions", "courses", "fees", "placements", "campus", "facilities",
    "hostel", "library", "principal", "location", "contact", "faculty", "hod", "staff",
    "rules", "exams", "scholarship", "bus", "wifi", "sports", "history", "agriculture",
    "fisheries", "bba", "computer science", "food technology", "fsn"
]

# =====================================================
# MAIN COLLEGE DATABASE
# =====================================================
COLLEGE_DATABASE = {
    "metadata": {
        "college_name_en": "Ideal College of Arts and Sciences",
        "college_name_te": "ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్",
        "location": "Vidyuth Nagar, Kakinada, Andhra Pradesh",
        "affiliation": "Adikavi Nannaya University",
        "accreditation": "NAAC 'A' Grade",
        "languages_supported": ["en", "te"],
        "last_updated": "April 2026"
    },

    "sections": {

        "general_information": {
            "keywords_en": ["college name", "location", "principal", "timings", "contact", "strength"],
            "keywords_te": ["కాలేజీ పేరు", "స్థానం", "ప్రిన్సిపల్"],
            "data": {
                "en": {
                    "name": "Ideal College of Arts and Sciences",
                    "location": "Vidyuth Nagar, Kakinada, Andhra Pradesh",
                    "principal": "Dr. T. Satyanarayana",
                    "vice_principal": "Mr. V. Kama Raju",
                    "academic_director": "Ranjith Sir",
                    "administrative_director": "Vasu Sir",
                    "college_timings": "9:30 AM - 3:45 PM (Monday to Saturday)",
                    "lunch_break": "1:00 PM - 1:45 PM",
                    "contact": "0884-2384382 / 0884-2384381",
                    "email": "idealcolleges@gmail.com",
                    "website": "https://idealcollege.edu.in",
                    "college_strength": "1200 students (including Junior + Senior)"
                }
            }
        },

        "governance_and_administration": {
            "keywords_en": ["administration", "principal", "directors", "exam cell"],
            "keywords_te": ["నిర్వహణ"],
            "data": {
                "en": {
                    "academic_director": "Ranjith Sir",
                    "administrative_director": "Vasu Sir",
                    "exam_incharge": "Mr. K. Suresh Kumar"
                }
            }
        },

        "courses": {
            "keywords_en": ["courses", "ug", "pg"],
            "keywords_te": ["కోర్సులు"],
            "data": {
                "en": {
                    "ug": ["B.Sc Computers", "BCA", "B.Sc AI", "BBA", "Agriculture", "Food Technology", "Aqua & Fisheries"],
                    "pg": ["MCA", "M.Sc Organic Chemistry", "M.Sc Analytical Chemistry", "M.Sc Food Science & Technology", "M.Sc Aquaculture"],
                    "ug_duration": "3 Years",
                    "pg_duration": "2 Years"
                }
            }
        },

        "fee_structure": {
            "keywords_en": ["fees", "fee structure"],
            "keywords_te": ["ఫీజులు"],
            "data": {
                "en": {
                    "range": "₹45,000 - ₹60,000 per year",
                    "bsc_computers": "₹50,000/year",
                    "bca": "₹50,000/year",
                    "bsc_ai": "₹50,000/year",
                    "bba": "₹50,000/year",
                    "agriculture": "₹55,000/year",
                    "food_technology": "₹60,000/year",
                    "aqua_fisheries": "₹45,000/year"
                }
            }
        },

        "hostel_and_amenities": {
            "keywords_en": ["hostel", "hostel fee"],
            "keywords_te": ["హాస్టల్"],
            "data": {
                "en": {
                    "available": True,
                    "fee": "₹60,000 per year",
                    "features": ["Separate Boys & Girls Hostels", "Mess Facility (Breakfast, Lunch, Dinner)", "Warden Supervision"]
                }
            }
        },

        "transport": {
            "keywords_en": ["bus", "transport"],
            "keywords_te": ["బస్సు"],
            "data": {
                "en": "Bus facility available from various areas in and around Kakinada."
            }
        },

        "library": {
            "keywords_en": ["library"],
            "keywords_te": ["లైబ్రరీ"],
            "data": {
                "en": {
                    "librarian": "Mrs. K. Vara Lakshmi",
                    "timing": "9:30 AM - 3:45 PM",
                    "features": "Textbooks, Journals, E-resources"
                }
            }
        },

        "examinations": {
            "keywords_en": ["exams", "attendance"],
            "keywords_te": ["పరీక్షలు"],
            "data": {
                "en": {
                    "minimum_attendance": "75%",
                    "system": "Internal + University Semester exams"
                }
            }
        },

        "campus_facilities": {
            "keywords_en": ["labs", "wifi", "playground", "cafeteria", "cctv"],
            "keywords_te": ["సదుపాయాలు"],
            "data": {
                "en": ["Computer Labs", "Science Labs", "Wi-Fi", "Playground", "Cafeteria", "RO Water", "24/7 CCTV", "Parking"]
            }
        },

        "placements": {
            "keywords_en": ["placements", "selected", "companies", "drives", "2025", "2026"],
            "keywords_te": ["ప్లేస్‌మెంట్లు"],
            "data": {
                "en": {
                    "college_strength": "1200 students (including Junior + Senior)",
                    "statistics": {
                        "2025": {
                            "selected_students": 95
                        },
                        "2026": {
                            "seniors_drive": {
                                "visited_companies": 9,
                                "opportunity_companies": 9,
                                "students_participated": 362,
                                "students_selected": 329,
                                "branch_wise_participation": {
                                    "computer_science": 193,
                                    "bba": 85,
                                    "agriculture": 25
                                }
                            },
                            "passouts": 435
                        }
                    },
                    "companies_visited_physical": [
                        "Tech Mahindra",
                        "Sutherland",
                        "Concutix",
                        "Sagility",
                        "Teleperformance",
                        "Vidyant",
                        "Sand Space",
                        "First Source"
                    ],
                    "companies_online_exam": [
                        "TCS",
                        "Infosys",
                        "HCL",
                        "Cognizant",
                        "Intouch EX",
                        "L & T Mind Tree"
                    ],
                    "training": "CRT, Soft Skills, Aptitude, Spoken English, Mock Interviews",
                    "note": "Contact the Training & Placement Cell for latest detailed reports."
                }
            }
        },

        "faculty_and_departments": {
            "keywords_en": ["faculty", "hod", "staff", "teachers", "agriculture", "fisheries", "bba", "computer science"],
            "keywords_te": ["సిబ్బంది"],
            "data": {
                "en": {
                    "total_faculty": 54,
                    "departments": {
                        "agriculture": {
                            "name": "Department of Agriculture",
                            "hod": "K. Raju",
                            "faculty": [
                                {"name": "K. Raju", "designation": "HOD"},
                                {"name": "N. Mounica", "designation": "Assistant Professor"},
                                {"name": "A. Pavan Kumar", "designation": "Assistant Professor"},
                                {"name": "E. Anusha", "designation": "Assistant Professor"}
                            ]
                        },
                        "fisheries": {
                            "name": "Department of Fisheries",
                            "hod": "P. Lova Raju",
                            "faculty": [
                                {"name": "P. Lova Raju", "designation": "HOD"},
                                {"name": "D. Madhu", "designation": "Assistant Professor"},
                                {"name": "V. Ahalya", "designation": "Assistant Professor"},
                                {"name": "Md. Reshma", "designation": "Assistant Professor"},
                                {"name": "Ch. Neelima", "designation": "Assistant Professor"}
                            ]
                        },
                        "fsn_and_food_technology": {
                            "name": "Department of FSN & Food Technology",
                            "hods": {
                                "fsn": "S. Vinod Kumar",
                                "food_technology": "G. Deekshitha"
                            },
                            "faculty": [
                                {"name": "P. Prasanna", "designation": "Professor of Practice"},
                                {"name": "S. Vinod Kumar", "designation": "HOD - FSN"},
                                {"name": "G. Deekshitha", "designation": "HOD - Food Technology"},
                                {"name": "A. Lalitha", "designation": "Assistant Professor (FSN)"},
                                {"name": "K. Satya Srikshya", "designation": "Assistant Professor (FSN)"},
                                {"name": "G. Vasantha", "designation": "Assistant Professor (FT)"},
                                {"name": "Ch. Gnapika", "designation": "Assistant Professor (FT)"},
                                {"name": "P. Dasu Babu", "designation": "Assistant Professor (FT)"},
                                {"name": "K. D. Mahalakshmi Kalyani", "designation": "Assistant Professor (FT)"}
                            ]
                        },
                        "bba": {
                            "name": "Department of BBA",
                            "hod": "E. Srinilasa Rao",
                            "vice_principal": "V. Kama Raju",
                            "faculty": [
                                {"name": "V. Kama Raju", "designation": "Vice Principal"},
                                {"name": "E. Srinilasa Rao", "designation": "HOD"},
                                {"name": "M. Sasi Rekha", "designation": "Assistant Professor"},
                                {"name": "M. Pavana Kumari", "designation": "Assistant Professor"},
                                {"name": "V. Srinivas", "designation": "Assistant Professor"},
                                {"name": "K.V.S.L. Narashima Rao", "designation": "Assistant Professor"},
                                {"name": "S. Ramana", "designation": "Assistant Professor"},
                                {"name": "K. Mounika", "designation": "Assistant Professor"},
                                {"name": "N. Arjun Rao", "designation": "Assistant Professor"},
                                {"name": "P. Sirisha", "designation": "Assistant Professor"},
                                {"name": "G. Stephen", "designation": "Assistant Professor"}
                            ]
                        },
                        "computer_science": {
                            "name": "Department of Computer Science",
                            "hod": "V.S.V. Deepak",
                            "additional_hod": "M. Kameswara Rao",
                            "head_of_idc": "M.A. Sayeed",
                            "faculty": [
                                {"name": "M.A. Sayeed", "designation": "Head of IDC"},
                                {"name": "V.S.V. Deepak", "designation": "Head of the Department"},
                                {"name": "M. Kameswara Rao", "designation": "Additional Head of the Department"},
                                {"name": "V. Jeevan Kanth", "designation": "Assistant Professor"},
                                {"name": "T. Pridhvi Krishna", "designation": "Assistant Professor"},
                                {"name": "B. Venkata Ratnam", "designation": "Assistant Professor"},
                                {"name": "K. Macha Rao", "designation": "Assistant Professor"},
                                {"name": "P. Vidyadar Reddy", "designation": "Assistant Professor"},
                                {"name": "A. Thulasi", "designation": "Assistant Professor"},
                                {"name": "K. Prabhakar", "designation": "Assistant Professor"},
                                {"name": "K. Srilaxmi", "designation": "Assistant Professor"},
                                {"name": "V. Raj Kumar", "designation": "Assistant Professor"},
                                {"name": "P.N. Jyoshna Sree", "designation": "Assistant Professor"},
                                {"name": "S. Laxmi Prasanna", "designation": "Assistant Professor"},
                                {"name": "M. Jeeela Rathanam", "designation": "Assistant Professor"}
                            ]
                        }
                    },
                    "support_staff": {
                        "soft_skills": [
                            {"name": "Y. Harini", "designation": "Soft Skills Trainer"},
                            {"name": "P. Pooja", "designation": "Soft Skills Trainer"}
                        ],
                        "competitive_exams": [
                            {"name": "M. Leela Mohan Krishna", "designation": "Competitive Exam Trainer"},
                            {"name": "K. Rambabu", "designation": "Competitive Exam Trainer"},
                            {"name": "P. Kiran Kumar", "designation": "Competitive Exam Trainer"},
                            {"name": "K. Satish Kumar", "designation": "Competitive Exam Trainer"}
                        ],
                        "librarian": [
                            {"name": "K. Vara Lakshmi", "designation": "Librarian"}
                        ],
                        "telugu": [
                            {"name": "Dr. V.V. Satya Narayana", "designation": "Assistant Professor of Telugu"}
                        ]
                    }
                }
            }
        },

        "crt_and_soft_skills": {
            "keywords_en": ["crt", "soft skills", "spoken english"],
            "data": {
                "en": "Dedicated training in CRT, Soft Skills, Spoken English and Competitive Exams"
            }
        },

        "sports_and_activities": {
            "keywords_en": ["sports", "nss", "ncc", "cultural"],
            "data": {
                "en": ["Cricket", "Volleyball", "Badminton", "NSS", "NCC", "Cultural Events"]
            }
        },

        "student_rules": {
            "keywords_en": ["rules", "uniform", "ragging"],
            "data": {
                "en": {
                    "uniform": "College uniform and ID card are compulsory",
                    "ragging": "Strictly prohibited with zero tolerance",
                    "mobile": "Mobile phones restricted during class hours",
                    "attendance": "Minimum 75% attendance mandatory"
                }
            }
        },

        "health_and_safety": {
            "keywords_en": ["safety", "cctv", "medical"],
            "data": {
                "en": "24/7 CCTV surveillance, First Aid facility and Security"
            }
        },

        "admissions": {
            "keywords_en": ["admission", "eligibility", "documents"],
            "data": {
                "en": {
                    "ug_eligibility": "Passed Intermediate (10+2)",
                    "pg_eligibility": "Relevant Bachelor's Degree",
                    "documents_required": ["10th Memo", "12th Memo", "Transfer Certificate", "Aadhaar", "Photos"]
                }
            }
        },

        "historical_journey": {
            "keywords_en": ["history", "founders"],
            "data": {
                "en": {
                    "established": "Junior College (1970), Degree College (1974)",
                    "founders": ["Dr. Col. D. S. Raju", "Dr. P. V. N. Raju", "Dr. P. Chiranjeevini Kumari", "Dr. N. S. R. Sastry"]
                }
            }
        },

        "ai_responses": {
            "keywords_en": ["about college", "placements", "courses"],
            "data": {
                "en": {
                    "about_college": "Ideal College is a NAAC 'A' Grade institution with 1200 students and excellent placements.",
                    "placements": "In 2026, 329 students were selected from 362 participants.",
                    "courses": "UG & PG courses in Computers, BBA, Agriculture, Food Technology & Fisheries."
                }
            }
        }
    }
}
# =====================================================
# ✅ FINAL FIX (DO NOT REMOVE / DO NOT MODIFY ABOVE DATA)
# =====================================================

def _safe_string(text):
    """Safe string function to handle braces in f-strings"""
    if text is None:
        return ""
    return str(text).replace("{", "{{").replace("}", "}}")

# ====================== COLLEGE INFORMATION ======================

college_info_en = f"""
{_safe_string(COLLEGE_NAME)} is a reputed educational institution 
offering various undergraduate and postgraduate courses in Arts, Sciences, and Commerce.
"""

college_info_te = f"""
{_safe_string(COLLEGE_NAME)} ఒక ప్రముఖ విద్యా సంస్థ. 
ఇక్కడ ఆర్ట్స్, సైన్సెస్, కామర్స్ విభాగాల్లో అండర్ గ్రాడ్యుయేట్ & పోస్ట్ గ్రాడ్యుయేట్ కోర్సులు అందుబాటులో ఉన్నాయి.
"""

# Final college summary dictionary
COLLEGE_SUMMARY = {
    "name": COLLEGE_NAME,
    "phone": COLLEGE_PHONE,
    "email": COLLEGE_EMAIL,
    "website": COLLEGE_WEBSITE,
    "location": COLLEGE_LOCATION,
    "description_en": college_info_en,
    "description_te": college_info_te,
    "established": "1970",
    "courses": ["B.Sc Computers", "BCA", "B.Sc AI", "BBA", "Agriculture", "Food Technology", "Aqua & Fisheries", "MCA", "M.Sc Organic Chemistry", "M.Sc Analytical Chemistry", "M.Sc Food Science & Technology", "M.Sc Aquaculture"]
}

def get_college_summary():
    return {
        "name": COLLEGE_NAME,
        "contact": COLLEGE_PHONE,
        "email": COLLEGE_EMAIL,
        "website": COLLEGE_WEBSITE,
        "location": COLLEGE_LOCATION,
        "summary": college_info_en.strip()
    }