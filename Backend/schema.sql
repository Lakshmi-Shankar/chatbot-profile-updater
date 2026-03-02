-- students table
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    phone TEXT,
    date_of_birth TEXT,
    city TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- education_details table
CREATE TABLE education_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL UNIQUE,
    tenth_board TEXT,
    tenth_percentage INTEGER,
    twelfth_board TEXT,
    twelfth_percentage INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- courses table
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    duration_months INTEGER,
    fee INTEGER
);

CREATE INDEX courses_title_index ON courses(title);

-- applications table
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT CHECK(
        status IN ('submitted','under_review','accepted','rejected')
    ) NOT NULL DEFAULT 'submitted',
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE INDEX applications_status_index ON applications(status);