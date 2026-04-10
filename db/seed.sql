USE college_network;

-- Departments
INSERT INTO departments (name) VALUES
  ('Computer Science'), ('Electronics'), ('Mechanical'),
  ('Civil'), ('Mathematics'), ('Physics');

-- Clubs
INSERT INTO clubs (name, description) VALUES
  ('Coding Club',       'Competitive programming and hackathons'),
  ('Robotics Club',     'Build and battle robots'),
  ('Drama Society',     'Theatre and performing arts'),
  ('Photography Club',  'Shoots, exhibitions, darkroom'),
  ('Music Club',        'Bands, jam sessions, college fest');

-- Persons
INSERT INTO persons (name, email, year, dept_id, hostel, bio, roles) VALUES
  ('Arjun Sharma',   'arjun@college.edu',   2, 1, 'Hostel A', 'Loves CP and coffee', 'student'),
  ('Priya Mehta',    'priya@college.edu',   3, 1, 'Hostel B', 'Full-stack dev, DSA nerd', 'student'),
  ('Rohit Verma',    'rohit@college.edu',   2, 2, 'Hostel A', 'Electronics + ML combo', 'student'),
  ('Sneha Iyer',     'sneha@college.edu',   4, 3, 'Hostel C', 'Mechanical with a passion for design', 'student'),
  ('Karan Joshi',    'karan@college.edu',   1, 1, 'Hostel B', 'Freshman, figuring things out', 'student'),
  ('Meera Pillai',   'meera@college.edu',   3, 4, 'Hostel D', 'Civil but codes on weekends', 'student'),
  ('Dev Nair',       'dev@college.edu',     2, 5, 'Hostel A', 'Math olympiad finalist', 'student'),
  ('Ananya Singh',   'ananya@college.edu',  4, 1, 'Hostel C', 'AI researcher wannabe', 'student'),
  ('Varun Khanna',   'varun@college.edu',   3, 2, 'Hostel B', 'Into robotics and guitar', 'student'),
  ('Tanya Bose',     'tanya@college.edu',   1, 6, 'Hostel D', 'Physics + photography', 'student');

-- Courses
INSERT INTO courses (code, name, dept_id) VALUES
  ('CS201', 'Data Structures',        1),
  ('CS301', 'DBMS',                   1),
  ('CS401', 'Machine Learning',       1),
  ('EC201', 'Digital Circuits',       2),
  ('MA201', 'Linear Algebra',         5),
  ('ME301', 'Thermodynamics',         3);

-- Enrollments
INSERT INTO course_enrollments (person_id, course_id, semester) VALUES
  (1,1,'2024-odd'),(1,2,'2024-odd'),(2,2,'2024-odd'),(2,3,'2024-even'),
  (3,1,'2024-odd'),(3,4,'2024-odd'),(5,1,'2024-odd'),(5,2,'2024-odd'),
  (7,5,'2024-odd'),(8,3,'2024-even'),(9,4,'2024-odd');

-- Club memberships
INSERT INTO club_memberships (person_id, club_id, role, member_status, joined_on) VALUES
  (1,1,'Member',    'active',     '2023-08-01'),
  (2,1,'Lead',      'active',     '2022-08-01'),
  (3,2,'Member',    'active',     '2023-08-01'),
  (9,2,'Co-Lead',   'active',     '2022-08-01'),
  (4,3,'Member',    'active',     '2023-01-01'),
  (6,3,'Director',  'passed_out', '2021-08-01'),
  (10,4,'Member',   'active',     '2024-01-01'),
  (7,4,'Member',    'active',     '2023-08-01'),
  (9,5,'Guitarist', 'active',     '2022-01-01'),
  (8,1,'Member',    'active',     '2023-08-01');

-- Relationships (graph edges)
INSERT INTO relationships (person_a, person_b, rel_type, strength, since, notes) VALUES
  (1,2,'friend',            8,'2023-09-01','Met at coding club'),
  (1,3,'hostel_neighbour',  6,'2023-07-01','Same hostel wing'),
  (1,5,'mentor',            9,'2024-01-15','Arjun mentors Karan in DSA'),
  (2,8,'classmate',         7,'2023-08-01','DBMS class together'),
  (2,5,'classmate',         5,'2024-08-01','Both in CS201'),
  (3,9,'friend',            8,'2023-08-01','Robotics club buddies'),
  (4,6,'project_teammate',  7,'2023-11-01','Worked on bridge design project'),
  (6,7,'acquaintance',      3,'2024-01-01','Met at fest'),
  (7,10,'friend',           6,'2023-09-15','Photography club'),
  (8,2,'friend',            9,'2022-09-01','Senior-junior friendship'),
  (9,3,'classmate',         6,'2023-08-01','EC201 together'),
  (1,7,'acquaintance',      4,'2024-02-01','Met at math talk'),
  (5,3,'hostel_neighbour',  5,'2023-07-01','Same hostel'),
  (2,9,'acquaintance',      4,'2023-10-01','College fest');

-- Events
INSERT INTO events (name, event_date, location, club_id) VALUES
  ('HackNight 2024',     '2024-03-15', 'CS Lab',         1),
  ('RoboWars 2024',      '2024-02-10', 'Main Ground',    2),
  ('Annual Drama Fest',  '2024-01-20', 'Auditorium',     3),
  ('Photo Walk',         '2024-03-01', 'Campus',         4);

-- Attendance
INSERT INTO event_attendance (person_id, event_id) VALUES
  (1,1),(2,1),(5,1),(8,1),(3,2),(9,2),(4,3),(6,3),(7,4),(10,4),(1,4);
