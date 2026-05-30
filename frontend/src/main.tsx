import React, { FormEvent, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

type ApiList<T> = T[] | { results: T[] };
type ApiState = 'connected' | 'locked' | 'offline';
type EntityKey = 'teachers' | 'students' | 'groups' | 'payments' | 'attendances' | 'salaries' | 'centers';

type Teacher = {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  status: string;
  hourly_rate: string;
  hire_date: string;
  user?: number | null;
  assigned_groups?: number[];
};

type Student = {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  parent_phone?: string;
  group: number | null;
  group_name?: string;
  status: string;
  enrollment_date: string;
};

type Group = {
  id: number;
  name: string;
  level: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  schedules?: GroupSchedule[];
  teacher: number | null;
  teacher_name?: string;
  schedule_display?: string;
  students_count: number;
  paid_students_count?: number;
  unpaid_students_count?: number;
  max_students: number;
  available_seats: number;
  tuition_fee: string;
  is_active: boolean;
};

type GroupSchedule = {
  id?: number;
  day_of_week: string;
  day_display?: string;
  start_time: string;
  end_time: string;
};

type Payment = {
  id: number;
  student: number;
  student_name: string;
  group: number | null;
  group_name?: string;
  amount: string;
  month: string;
  status: string;
  payment_method: string;
};

type Attendance = {
  id: number;
  student: number;
  student_name: string;
  group: number;
  group_name: string;
  date: string;
  status: string;
  status_display: string;
  homework_status: string;
  homework_status_display: string;
  homework_note?: string;
  is_present: boolean;
};

type Salary = {
  id: number;
  teacher: number;
  teacher_name: string;
  month: string;
  teaching_hours: string;
  hourly_rate: string;
  bonus: string;
  deductions: string;
  total_salary: string;
  is_paid: boolean;
};

type Center = {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  currency: string;
  default_tuition_fee: string;
};

type PlatformData = {
  teachers: Teacher[];
  students: Student[];
  groups: Group[];
  payments: Payment[];
  attendances: Attendance[];
  salaries: Salary[];
  centers: Center[];
};

type Session = {
  authenticated: boolean;
  is_operator: boolean;
  is_teacher: boolean;
  role: string;
  username: string;
  full_name: string;
};

type PublicStudent = {
  id: number;
  full_name: string;
  payment_paid: boolean;
  payment_status: string;
  payment_month: string;
  attendance_status: string;
  attendance_date: string;
  homework_status: string;
  homework_status_display: string;
};

type PublicGroup = {
  id: number;
  name: string;
  level: string;
  teacher_name: string;
  schedule_display: string;
  tuition_fee: string;
  students_count: number;
  paid_students_count: number;
  present_students_count: number;
  homework_done_count: number;
  students: PublicStudent[];
};

type PublicData = {
  center: Center | null;
  current_month?: string;
  groups: PublicGroup[];
};

const emptyData: PlatformData = {
  teachers: [],
  students: [],
  groups: [],
  payments: [],
  attendances: [],
  salaries: [],
  centers: [],
};

const entityConfig: Record<EntityKey, { label: string; endpoint: string }> = {
  teachers: { label: "O'qituvchilar", endpoint: '/api/teachers/' },
  students: { label: "O'quvchilar", endpoint: '/api/students/' },
  groups: { label: 'Guruhlar', endpoint: '/api/groups/' },
  payments: { label: "To'lovlar", endpoint: '/api/payments/' },
  attendances: { label: 'Davomat', endpoint: '/api/attendances/' },
  salaries: { label: "O'qituvchi oyligi", endpoint: '/api/teacher-salaries/' },
  centers: { label: 'Markaz sozlamasi', endpoint: '/api/learning-centers/' },
};

const navItems: Array<{ id: 'overview' | EntityKey; label: string }> = [
  { id: 'overview', label: 'Dashboard' },
  { id: 'students', label: "O'quvchilar" },
  { id: 'groups', label: 'Guruhlar' },
  { id: 'teachers', label: "O'qituvchilar" },
  { id: 'payments', label: "To'lovlar" },
  { id: 'attendances', label: 'Davomat' },
  { id: 'salaries', label: 'Oyliklar' },
  { id: 'centers', label: 'Markaz' },
];

function normalize<T>(payload: ApiList<T>): T[] {
  return Array.isArray(payload) ? payload : payload.results;
}

function getCookie(name: string) {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1] || '';
}

async function ensureCsrfCookie() {
  if (!getCookie('csrftoken')) {
    await fetch('/api/auth/session/', { credentials: 'include' });
  }
}

async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const method = String(options.method || 'GET').toUpperCase();
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    await ensureCsrfCookie();
  }

  const response = await fetch(url, {
    credentials: 'include',
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const detail = await parseError(response);
    throw new Error(detail || response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

async function parseError(response: Response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    const payload = await response.json();
    if (payload.detail) return String(payload.detail);
    return Object.entries(payload)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`)
      .join(' | ');
  }
  return response.text();
}

async function fetchList<T>(url: string): Promise<T[]> {
  return normalize<T>(await apiFetch<ApiList<T>>(url));
}

function money(value: string | number) {
  return `${Number(value || 0).toLocaleString('uz-UZ')} so'm`;
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function App() {
  const [active, setActive] = useState<'overview' | EntityKey>('overview');
  const [data, setData] = useState<PlatformData>(emptyData);
  const [publicData, setPublicData] = useState<PublicData>({ center: null, groups: [] });
  const [session, setSession] = useState<Session>({ authenticated: false, is_operator: false, is_teacher: false, role: '', username: '', full_name: '' });
  const [apiState, setApiState] = useState<ApiState>('offline');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  async function loadAll() {
    setLoading(true);
    try {
      const sessionState = await apiFetch<Session>('/api/auth/session/');
      setSession(sessionState);

      if (!sessionState.is_operator && !sessionState.is_teacher) {
        setData(emptyData);
        setApiState('locked');
        setPublicData(await apiFetch<PublicData>('/api/public/'));
        return;
      }

      const [groups, students, payments, attendances] = await Promise.all([
        fetchList<Group>(entityConfig.groups.endpoint),
        fetchList<Student>(entityConfig.students.endpoint),
        fetchList<Payment>(entityConfig.payments.endpoint),
        fetchList<Attendance>(entityConfig.attendances.endpoint),
      ]);

      const [teachers, salaries, centers] = sessionState.is_operator
        ? await Promise.all([
            fetchList<Teacher>(entityConfig.teachers.endpoint),
            fetchList<Salary>(entityConfig.salaries.endpoint),
            fetchList<Center>(entityConfig.centers.endpoint),
          ])
        : [[], [], []] as [Teacher[], Salary[], Center[]];

      setData({ teachers, students, groups, payments, attendances, salaries, centers });
      setApiState('connected');
    } catch (error) {
      setApiState('offline');
      setMessage("Backend bilan ulanishda xatolik. Django server 8000-portda ishlayotganini tekshiring.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  const totals = useMemo(() => {
    const paid = data.payments.filter((payment) => payment.status === 'paid').length;
    const pending = data.payments.filter((payment) => payment.status !== 'paid').length;
    return {
      teachers: data.teachers.length,
      students: data.students.length,
      groups: data.groups.length,
      paid,
      pending,
    };
  }, [data]);

  async function handleLogout() {
    setSession({ authenticated: false, is_operator: false, is_teacher: false, role: '', username: '', full_name: '' });
    setApiState('locked');
    setData(emptyData);
    setActive('overview');
    setMessage('');

    try {
      await apiFetch('/api/auth/logout/', { method: 'POST', body: '{}' });
    } catch (error) {
      console.warn('Logout request failed after local sign-out:', error);
    }
  }

  const visibleNavItems = session.is_teacher
    ? navItems.filter((item) => ['overview', 'groups', 'students', 'attendances'].includes(item.id))
    : navItems;

  return (
    <div className={session.authenticated ? 'app' : 'app publicApp'}>
      {session.authenticated && (
        <aside className="sidebar">
          <div className="brand">
            <div className="brandMark">SL</div>
            <div>
              <strong>Status LC</strong>
              <span>{session.is_teacher ? "O'qituvchi kabinet" : 'Operator kabinet'}</span>
            </div>
          </div>

          <nav className="nav">
            {visibleNavItems.map((item) => (
              <button
                key={item.id}
                className={active === item.id ? 'navButton active' : 'navButton'}
                onClick={() => setActive(item.id)}
              >
                <span className="navDot" />
                {item.label}
              </button>
            ))}
          </nav>
        </aside>
      )}

      <main className={session.authenticated ? 'main' : 'main publicMain'}>
        {session.authenticated && (
          <header className="topbar">
            <div>
              <p className="eyebrow">Status LC operations</p>
              <h1>{session.is_teacher ? "O'qituvchi kabineti" : 'Operator boshqaruv kabineti'}</h1>
            </div>
            <div className="topbarActions">
              <div className={`apiBadge ${apiState}`}>
                {loading ? 'Yuklanmoqda' : apiState === 'connected' ? session.username : apiState === 'locked' ? 'Login kerak' : 'Offline'}
              </div>
              <button className="logoutButton" type="button" onClick={handleLogout}>
                Chiqish
              </button>
            </div>
          </header>
        )}

        {message && <div className="notice">{message}</div>}
        {!session.authenticated ? <PublicHome publicData={publicData} onLogin={loadAll} /> : session.is_teacher ? (
          <TeacherCabinet active={active} data={data} onChanged={loadAll} setMessage={setMessage} />
        ) : (
          <>
            {active === 'overview' && <Overview totals={totals} data={data} />}
            {active !== 'overview' && (
              <EntityManager
                entity={active}
                data={data}
                onChanged={loadAll}
                setMessage={setMessage}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

function LoginPanel({ onLogin }: { onLogin: () => Promise<void> }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    try {
      await apiFetch('/api/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      await onLogin();
    } catch {
      setError("Login yoki parol noto'g'ri, yoki foydalanuvchi kabinetga ruxsatga ega emas.");
    }
  }

  return (
    <section className="loginPanel">
      <div className="loginCopy">
        <p className="eyebrow dark">Kabinet login</p>
        <h2>Tizim kabinetiga kirish</h2>
        <p>Operator markazni boshqaradi, o'qituvchi esa o'z guruhlari va davomatini yuritadi.</p>
      </div>
      <form className="formGrid" onSubmit={submit}>
        <label>
          Login
          <input value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          Parol
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error && <p className="formError">{error}</p>}
        <button className="primaryButton" type="submit">Kirish</button>
      </form>
    </section>
  );
}

function PublicHome({ publicData, onLogin }: { publicData: PublicData; onLogin: () => Promise<void> }) {
  const center = publicData.center;
  const totalStudents = publicData.groups.reduce((sum, group) => sum + group.students_count, 0);
  const totalPaid = publicData.groups.reduce((sum, group) => sum + group.paid_students_count, 0);
  const totalPresent = publicData.groups.reduce((sum, group) => sum + group.present_students_count, 0);
  const totalHomework = publicData.groups.reduce((sum, group) => sum + group.homework_done_count, 0);

  return (
    <div className="publicLayout">
      <section className="heroPanel">
        <div>
          <p className="eyebrow dark">Mehmon sahifasi</p>
          <h2>{center?.name || 'Status LC'}</h2>
          <p>{center?.description || "O'quv markazi guruhlari, dars jadvali, davomat va to'lov holatlari haqida umumiy ma'lumot."}</p>
        </div>
        <div className="heroSeal">
          <span>{publicData.groups.length}</span>
          <small>Guruhlar</small>
        </div>
      </section>

      <section className="statsGrid">
        <Metric title="Guruhlar" value={publicData.groups.length} note="Faol guruhlar" />
        <Metric title="O'quvchilar" value={totalStudents} note="Jami ro'yxat" />
        <Metric title="To'lagan" value={totalPaid} note="Joriy oy" tone="gold" />
        <Metric title="Vazifa" value={totalHomework} note="Bajarganlar" />
      </section>

      <section className="contentGrid">
        <div className="tableCard">
          <div className="sectionHeader">
            <h2>Guruhlar</h2>
            <span>{totalPresent} ta kelgan</span>
          </div>
          <div className="groupCards compact">
            {publicData.groups.map((group) => (
              <article className="groupCard" key={group.id}>
                <div className="groupTop">
                  <div>
                    <h3>{group.name}</h3>
                    <p>{group.teacher_name || "O'qituvchi biriktirilmagan"}</p>
                  </div>
                  <span>{group.level}</span>
                </div>
                <div className="groupMeta">
                  <span>{group.schedule_display || 'Jadval yoq'}</span>
                  <span>{group.students_count} o'quvchi</span>
                  <span>{money(group.tuition_fee)}</span>
                </div>
                <div className="publicSummary">
                  <Badge value={`${group.present_students_count} kelgan`} ok={group.present_students_count > 0} />
                  <Badge value={`${group.homework_done_count} vazifa`} ok={group.homework_done_count > 0} />
                  <Badge value={`${group.paid_students_count} to'lov`} ok={group.paid_students_count > 0} />
                </div>
                <div className="table">
                  {group.students.map((student) => (
                    <div className="tableRow publicStudentRow" key={student.id}>
                      <strong>{student.full_name}</strong>
                      <span>{student.attendance_status}{student.attendance_date ? ` (${student.attendance_date})` : ''}</span>
                      <Badge value={student.homework_status_display || 'Tekshirilmagan'} ok={student.homework_status === 'done'} />
                      <Badge value={student.payment_status || (student.payment_paid ? "To'langan" : 'Kutilmoqda')} ok={student.payment_paid} />
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
        <LoginPanel onLogin={onLogin} />
      </section>
    </div>
  );
}

function TeacherCabinet({ active, data, onChanged, setMessage }: { active: 'overview' | EntityKey; data: PlatformData; onChanged: () => Promise<void>; setMessage: (message: string) => void }) {
  const [groupId, setGroupId] = useState(data.groups[0]?.id ? String(data.groups[0].id) : '');
  const [date, setDate] = useState(today());
  const [saving, setSaving] = useState(false);
  const selectedGroup = data.groups.find((group) => String(group.id) === groupId) || data.groups[0];
  const students = selectedGroup ? data.students.filter((student) => student.group === selectedGroup.id) : [];
  const [statuses, setStatuses] = useState<Record<number, string>>({});
  const [homeworkStatuses, setHomeworkStatuses] = useState<Record<number, string>>({});

  useEffect(() => {
    if (!groupId && data.groups[0]) {
      setGroupId(String(data.groups[0].id));
    }
  }, [data.groups, groupId]);

  useEffect(() => {
    const current: Record<number, string> = {};
    const homework: Record<number, string> = {};
    students.forEach((student) => {
      const existing = data.attendances.find((attendance) => attendance.student === student.id && attendance.date === date);
      current[student.id] = existing?.status || 'present';
      homework[student.id] = existing?.homework_status || 'not_checked';
    });
    setStatuses(current);
    setHomeworkStatuses(homework);
  }, [selectedGroup?.id, date, data.attendances.length]);

  async function saveAttendance(event: FormEvent) {
    event.preventDefault();
    if (!selectedGroup) return;
    setSaving(true);
    setMessage('');
    try {
      for (const student of students) {
        const existing = data.attendances.find((attendance) => attendance.student === student.id && attendance.group === selectedGroup.id && attendance.date === date);
        await apiFetch(existing ? `/api/attendances/${existing.id}/` : '/api/attendances/', {
          method: existing ? 'PATCH' : 'POST',
          body: JSON.stringify({
            student: student.id,
            group: selectedGroup.id,
            date,
            status: statuses[student.id] || 'present',
            homework_status: homeworkStatuses[student.id] || 'not_checked',
          }),
        });
      }
      setMessage('Davomat saqlandi.');
      await onChanged();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Davomatni saqlashda xatolik yuz berdi.');
    } finally {
      setSaving(false);
    }
  }

  const attendanceForm = (
    <TeacherAttendanceForm
      groups={data.groups}
      students={students}
      groupId={groupId}
      date={date}
      statuses={statuses}
      homeworkStatuses={homeworkStatuses}
      saving={saving}
      selectedGroup={selectedGroup}
      setGroupId={setGroupId}
      setDate={setDate}
      setStatuses={setStatuses}
      setHomeworkStatuses={setHomeworkStatuses}
      saveAttendance={saveAttendance}
    />
  );

  if (active === 'groups') {
    return <Groups groups={data.groups} />;
  }

  if (active === 'students') {
    return <TeacherStudents students={data.students} />;
  }

  if (active === 'attendances') {
    return (
      <section className="contentGrid">
        {attendanceForm}
        <TeacherAttendanceHistory attendances={data.attendances} />
      </section>
    );
  }

  return (
    <>
      <section className="heroPanel">
        <div>
          <p className="eyebrow dark">O'qituvchi kabineti</p>
          <h2>Mening guruhlarim</h2>
          <p>O'qituvchi o'ziga biriktirilgan guruhlar, o'quvchilar va davomat yozuvlarini boshqaradi.</p>
        </div>
        <div className="heroSeal">
          <span>{data.groups.length}</span>
          <small>Guruh</small>
        </div>
      </section>

      <section className="contentGrid">
        <Groups groups={data.groups} compact />
        {attendanceForm}
      </section>
    </>
  );
}

function TeacherAttendanceForm({
  groups,
  students,
  groupId,
  date,
  statuses,
  homeworkStatuses,
  saving,
  selectedGroup,
  setGroupId,
  setDate,
  setStatuses,
  setHomeworkStatuses,
  saveAttendance,
}: {
  groups: Group[];
  students: Student[];
  groupId: string;
  date: string;
  statuses: Record<number, string>;
  homeworkStatuses: Record<number, string>;
  saving: boolean;
  selectedGroup?: Group;
  setGroupId: (value: string) => void;
  setDate: (value: string) => void;
  setStatuses: React.Dispatch<React.SetStateAction<Record<number, string>>>;
  setHomeworkStatuses: React.Dispatch<React.SetStateAction<Record<number, string>>>;
  saveAttendance: (event: FormEvent) => Promise<void>;
}) {
  return (
    <form className="editorCard" onSubmit={saveAttendance}>
      <div className="sectionHeader">
        <h2>Davomat olish</h2>
        <span>{students.length} o'quvchi</span>
      </div>
      <div className="formGrid">
        <label>
          Guruh
          <select value={groupId} onChange={(event) => setGroupId(event.target.value)}>
            {groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}
          </select>
        </label>
        <label>
          Sana
          <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
        </label>
        <div className="attendanceList">
          {students.length ? students.map((student) => (
            <label className="attendanceLine" key={student.id}>
              <span>{student.full_name}</span>
              <select value={statuses[student.id] || 'present'} onChange={(event) => setStatuses((current) => ({ ...current, [student.id]: event.target.value }))}>
                {statusOptions.attendance.map((status) => <option key={status.value} value={status.value}>{status.label}</option>)}
              </select>
              <select value={homeworkStatuses[student.id] || 'not_checked'} onChange={(event) => setHomeworkStatuses((current) => ({ ...current, [student.id]: event.target.value }))}>
                {statusOptions.homework.map((status) => <option key={status.value} value={status.value}>{status.label}</option>)}
              </select>
            </label>
          )) : <div className="emptyState">Bu guruhda o'quvchi yo'q.</div>}
        </div>
        <button className="primaryButton" type="submit" disabled={saving || !selectedGroup || !students.length}>
          {saving ? 'Saqlanmoqda...' : 'Davomatni saqlash'}
        </button>
      </div>
    </form>
  );
}

function TeacherStudents({ students }: { students: Student[] }) {
  return (
    <section className="tableCard">
      <div className="sectionHeader">
        <h2>Mening o'quvchilarim</h2>
        <span>{students.length} ta o'quvchi</span>
      </div>
      <div className="table">
        {students.length ? students.map((student) => (
          <div className="tableRow detailRow" key={student.id}>
            <strong>{student.full_name}</strong>
            <span>{student.phone}</span>
            <span>{student.parent_phone || "Ota-ona telefoni yo'q"}</span>
            <Badge value={student.status} ok={student.status === 'active'} />
          </div>
        )) : <div className="emptyState">Sizga biriktirilgan o'quvchi yo'q.</div>}
      </div>
    </section>
  );
}

function TeacherAttendanceHistory({ attendances }: { attendances: Attendance[] }) {
  return (
    <section className="tableCard">
      <div className="sectionHeader">
        <h2>Davomat tarixi</h2>
        <span>{attendances.length} ta yozuv</span>
      </div>
      <div className="table">
        {attendances.length ? attendances.slice(0, 12).map((attendance) => (
          <div className="tableRow detailRow" key={attendance.id}>
            <strong>{attendance.student_name}</strong>
            <span>{attendance.group_name}</span>
            <span>{attendance.date}</span>
            <Badge value={attendance.status_display || attendance.status} ok={attendance.is_present} />
            <Badge value={attendance.homework_status_display || attendance.homework_status || 'Tekshirilmagan'} ok={attendance.homework_status === 'done'} />
          </div>
        )) : <div className="emptyState">Davomat yozuvi hali yo'q.</div>}
      </div>
    </section>
  );
}

function Overview({ totals, data }: { totals: { teachers: number; students: number; groups: number; paid: number; pending: number }; data: PlatformData }) {
  return (
    <>
      <section className="heroPanel">
        <div>
          <p className="eyebrow dark">Status LC</p>
          <h2>O'quv markazi boshqaruvi</h2>
          <p>Kundalik ishlar uchun o'quvchilar, guruhlar, o'qituvchilar, to'lovlar va davomat bitta joyda jamlangan.</p>
        </div>
        <div className="heroSeal">
          <span>{totals.groups}</span>
          <small>Faol guruhlar</small>
        </div>
      </section>

      <section className="statsGrid">
        <Metric title="O'quvchilar" value={totals.students} note="Jami ro'yxat" />
        <Metric title="Guruhlar" value={totals.groups} note="Darslar" />
        <Metric title="O'qituvchilar" value={totals.teachers} note="Jamoa" />
        <Metric title="Kutilmoqda" value={totals.pending} note="To'lov nazorati" tone="gold" />
      </section>

      <section className="contentGrid">
        <Groups groups={data.groups.slice(0, 3)} compact />
        <Payments payments={data.payments.slice(0, 4)} compact />
      </section>
    </>
  );
}

function Metric({ title, value, note, tone }: { title: string; value: number; note: string; tone?: 'gold' }) {
  return (
    <article className={tone === 'gold' ? 'metricCard gold' : 'metricCard'}>
      <span>{title}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function EntityManager({ entity, data, onChanged, setMessage }: { entity: EntityKey; data: PlatformData; onChanged: () => Promise<void>; setMessage: (message: string) => void }) {
  const [editing, setEditing] = useState<Record<string, unknown> | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [busy, setBusy] = useState(false);
  const records = data[entity] as Array<Record<string, unknown>>;
  const config = entityConfig[entity];

  useEffect(() => {
    setEditing(null);
    setSelectedGroup(null);
    setMessage('');
  }, [entity, setMessage]);

  async function remove(id: unknown) {
    if (!window.confirm("Yozuvni o'chirishni tasdiqlaysizmi?")) return;
    setBusy(true);
    try {
      await apiFetch(`${config.endpoint}${id}/`, { method: 'DELETE' });
      setMessage("Yozuv o'chirildi.");
      await onChanged();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Yozuvni o'chirishda xatolik yuz berdi.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="managerGrid">
      <div className="tableCard">
        <div className="sectionHeader">
          <h2>{config.label}</h2>
          <span>{records.length} ta yozuv</span>
        </div>
        {entity === 'groups' && selectedGroup ? (
          <GroupDetails
            group={selectedGroup}
            data={data}
            onBack={() => setSelectedGroup(null)}
            onEdit={() => setEditing(selectedGroup as unknown as Record<string, unknown>)}
          />
        ) : (
          <DataRows
            entity={entity}
            records={records}
            busy={busy}
            onEdit={setEditing}
            onDelete={remove}
            onOpen={entity === 'groups' ? (record) => {
              setSelectedGroup(record as unknown as Group);
              setEditing(record);
            } : undefined}
          />
        )}
      </div>
      <EditorPanel entity={entity} data={data} editing={editing} onCancel={() => setEditing(null)} onSaved={async () => {
        setEditing(null);
        setMessage('Yozuv saqlandi.');
        await onChanged();
      }} setMessage={setMessage} />
    </section>
  );
}

function DataRows({ entity, records, busy, onEdit, onDelete, onOpen }: { entity: EntityKey; records: Array<Record<string, unknown>>; busy: boolean; onEdit: (record: Record<string, unknown>) => void; onDelete: (id: unknown) => void; onOpen?: (record: Record<string, unknown>) => void }) {
  if (!records.length) return <div className="emptyState">Hali yozuv yo'q.</div>;

  return (
    <div className="table">
      {records.map((record) => (
        <div className={`tableRow actionRow ${entity}Row`} key={String(record.id)}>
          <RowSummary entity={entity} record={record} />
          <div className="rowActions">
            {onOpen && <button type="button" disabled={busy} onClick={() => onOpen(record)}>Ko'rish</button>}
            <button type="button" disabled={busy} onClick={() => onEdit(record)}>Tahrirlash</button>
            <button type="button" disabled={busy} className="dangerButton" onClick={() => onDelete(record.id)}>O'chirish</button>
          </div>
        </div>
      ))}
    </div>
  );
}

function GroupDetails({ group, data, onBack, onEdit }: { group: Group; data: PlatformData; onBack: () => void; onEdit: () => void }) {
  const students = data.students.filter((student) => student.group === group.id);
  const payments = data.payments.filter((payment) => payment.group === group.id);
  const attendances = data.attendances.filter((attendance) => attendance.group === group.id);
  const paidStudentIds = new Set(payments.filter((payment) => payment.status === 'paid').map((payment) => payment.student));
  const presentCount = attendances.filter((attendance) => attendance.is_present).length;
  const attendanceRate = attendances.length ? Math.round((presentCount / attendances.length) * 100) : 0;

  return (
    <div className="groupDetail">
      <div className="sectionHeader">
        <div>
          <h2>{group.name}</h2>
          <span>{group.teacher_name || "O'qituvchi biriktirilmagan"}</span>
        </div>
        <div className="sectionActions">
          <button type="button" onClick={onEdit}>Tahrirlash</button>
          <button type="button" onClick={onBack}>Orqaga</button>
        </div>
      </div>

      <div className="detailMetrics">
        <Metric title="O'quvchilar" value={students.length} note="Guruh ro'yxati" />
        <Metric title="To'lagan" value={paidStudentIds.size} note="To'lov yozuvlari" tone="gold" />
        <Metric title="Davomat" value={attendanceRate} note="Shu guruh bo'yicha %" />
      </div>

      <div className="detailInfo">
        <span><strong>Dars jadvali:</strong> {group.schedule_display || 'Kiritilmagan'}</span>
        <span><strong>Kurs puli:</strong> {money(group.tuition_fee)}</span>
        <span><strong>Bo'sh joy:</strong> {group.available_seats}</span>
      </div>

      <h3>O'quvchilar ro'yxati</h3>
      <div className="table">
        {students.length ? students.map((student) => (
          <div className="tableRow detailRow" key={student.id}>
            <strong>{student.full_name}</strong>
            <span>{student.phone}</span>
            <span>{student.parent_phone || "Ota-ona telefoni yo'q"}</span>
            <Badge value={paidStudentIds.has(student.id) ? "To'langan" : "Kutilmoqda"} ok={paidStudentIds.has(student.id)} />
          </div>
        )) : <div className="emptyState">Bu guruhda hali o'quvchi yo'q.</div>}
      </div>

      <h3>Guruh davomat yozuvlari</h3>
      <div className="table">
        {attendances.length ? attendances.slice(0, 8).map((attendance) => (
          <div className="tableRow detailRow" key={attendance.id}>
            <strong>{attendance.student_name}</strong>
            <span>{attendance.date}</span>
            <span>{attendance.group_name}</span>
            <Badge value={attendance.status_display || attendance.status} ok={attendance.is_present} />
            <Badge value={attendance.homework_status_display || attendance.homework_status || 'Tekshirilmagan'} ok={attendance.homework_status === 'done'} />
          </div>
        )) : <div className="emptyState">Bu guruh uchun davomat yozuvi hali yo'q.</div>}
      </div>
    </div>
  );
}

function RowSummary({ entity, record }: { entity: EntityKey; record: Record<string, unknown> }) {
  if (entity === 'teachers') return <><strong>{String(record.full_name || '')}</strong><span>{String(record.phone || '')}</span><span>{String(record.status || '')}</span></>;
  if (entity === 'students') return <><strong>{String(record.full_name || '')}</strong><span>{String(record.phone || '')}</span><span>{String(record.parent_phone || record.group_name || 'Guruhsiz')}</span></>;
  if (entity === 'groups') return <><strong>{String(record.name || '')}</strong><span>{String(record.level || '')}</span><span>{String(record.schedule_display || '')}</span></>;
  if (entity === 'payments') return <><strong>{String(record.student_name || '')}</strong><span>{money(String(record.amount || 0))}</span><Badge value={String(record.status || '')} /></>;
  if (entity === 'attendances') return <><strong>{String(record.student_name || '')}</strong><span>{String(record.date || '')}</span><Badge value={String(record.status_display || record.status || '')} ok={Boolean(record.is_present)} /><Badge value={String(record.homework_status_display || record.homework_status || 'Tekshirilmagan')} ok={record.homework_status === 'done'} /></>;
  if (entity === 'salaries') return <><strong>{String(record.teacher_name || '')}</strong><span>{String(record.month || '')}</span><span>{money(String(record.total_salary || 0))}</span></>;
  return <><strong>{String(record.name || '')}</strong><span>{String(record.phone || '')}</span><span>{String(record.currency || '')}</span></>;
}

function EditorPanel({ entity, data, editing, onCancel, onSaved, setMessage }: { entity: EntityKey; data: PlatformData; editing: Record<string, unknown> | null; onCancel: () => void; onSaved: () => Promise<void>; setMessage: (message: string) => void }) {
  const initial = useMemo(() => buildInitial(entity, editing), [entity, editing]);
  const [form, setForm] = useState<Record<string, string | boolean>>(initial);
  const [saving, setSaving] = useState(false);
  const config = entityConfig[entity];

  useEffect(() => {
    setForm(initial);
  }, [initial]);

  function update(name: string, value: string | boolean) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const missing = validateRequired(entity, form);
    if (missing) {
      setMessage(missing);
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      const payload = buildPayload(entity, form);
      const url = editing ? `${config.endpoint}${editing.id}/` : config.endpoint;
      await apiFetch(url, {
        method: editing ? 'PATCH' : 'POST',
        body: JSON.stringify(payload),
      });
      await onSaved();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Saqlashda xatolik yuz berdi.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="editorCard" onSubmit={submit}>
      <div className="sectionHeader">
        <h2>{editing ? `${config.label} tahrirlash` : `${config.label}: yangi`}</h2>
        {editing && <button type="button" onClick={onCancel}>Bekor qilish</button>}
      </div>
      <Fields entity={entity} form={form} data={data} update={update} />
      <button className="primaryButton" type="submit" disabled={saving}>
        {saving ? 'Saqlanmoqda...' : 'Saqlash'}
      </button>
    </form>
  );
}

function Fields({ entity, form, data, update }: { entity: EntityKey; form: Record<string, string | boolean>; data: PlatformData; update: (name: string, value: string | boolean) => void }) {
  const input = (name: string, label: string, type = 'text') => (
    <label>
      {label}
      <input type={type} value={String(form[name] ?? '')} onChange={(event) => update(name, event.target.value)} />
    </label>
  );
  const checkbox = (name: string, label: string) => (
    <label className="checkField">
      <input type="checkbox" checked={Boolean(form[name])} onChange={(event) => update(name, event.target.checked)} />
      {label}
    </label>
  );
  const select = (name: string, label: string, options: Array<{ value: string | number; label: string }>) => (
    <label>
      {label}
      <select value={String(form[name] ?? '')} onChange={(event) => update(name, event.target.value)}>
        <option value="">Tanlang</option>
        {options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
    </label>
  );

  if (entity === 'teachers') return (
    <div className="formGrid">
      {input('first_name', 'Ism')}
      {input('last_name', 'Familiya')}
      {input('email', 'Email', 'email')}
      {input('phone', 'Telefon')}
      {input('hire_date', 'Ish boshlagan sana', 'date')}
      {input('hourly_rate', 'Soatbay stavka', 'number')}
      {select('status', 'Status', statusOptions.teacher)}
      {!form.user && input('username', 'Kabinet login')}
      {input('password', form.user ? 'Yangi parol' : 'Kabinet paroli', 'password')}
      <div className="scheduleEditor">
        <strong>Biriktirilgan guruhlar</strong>
        {data.groups.length ? data.groups.map((group) => checkbox(`teacher_group_${group.id}`, group.name)) : <span className="mutedText">Hali guruh yo'q.</span>}
      </div>
    </div>
  );
  if (entity === 'students') return <div className="formGrid">{input('first_name', 'Ism')}{input('last_name', 'Familiya')}{input('phone', "O'quvchi telefoni")}{input('parent_phone', 'Ota-ona telefoni')}{select('group', 'Guruh', data.groups.map((g) => ({ value: g.id, label: g.name })))}{input('enrollment_date', "Ro'yxat sanasi", 'date')}{select('status', 'Status', statusOptions.student)}</div>;
  if (entity === 'groups') return (
    <div className="formGrid">
      {input('name', 'Guruh nomi')}
      {input('level', 'Daraja')}
      {select('teacher', "O'qituvchi", data.teachers.map((t) => ({ value: t.id, label: t.full_name })))}
      {input('max_students', "Sig'im", 'number')}
      {input('tuition_fee', "Oylik to'lov", 'number')}
      <div className="scheduleEditor">
        <strong>Dars kunlari va vaqti</strong>
        {days.map((day) => {
          const enabledKey = `schedule_${day.value}_enabled`;
          const startKey = `schedule_${day.value}_start`;
          const endKey = `schedule_${day.value}_end`;
          return (
            <div className="scheduleLine" key={day.value}>
              {checkbox(enabledKey, day.label)}
              <input
                type="time"
                value={String(form[startKey] ?? '18:00')}
                disabled={!form[enabledKey]}
                onChange={(event) => update(startKey, event.target.value)}
              />
              <input
                type="time"
                value={String(form[endKey] ?? '19:30')}
                disabled={!form[enabledKey]}
                onChange={(event) => update(endKey, event.target.value)}
              />
            </div>
          );
        })}
      </div>
      {checkbox('is_active', 'Faol')}
    </div>
  );
  if (entity === 'payments') return <div className="formGrid">{select('student', "O'quvchi", data.students.map((s) => ({ value: s.id, label: s.full_name })))}{select('group', 'Guruh', data.groups.map((g) => ({ value: g.id, label: g.name })))}{input('amount', 'Summa', 'number')}{input('month', 'Oy', 'date')}{select('status', 'Status', statusOptions.payment)}{select('payment_method', "To'lov turi", paymentMethods)}</div>;
  if (entity === 'attendances') return <div className="formGrid">{select('student', "O'quvchi", data.students.map((s) => ({ value: s.id, label: s.full_name })))}{select('group', 'Guruh', data.groups.map((g) => ({ value: g.id, label: g.name })))}{input('date', 'Sana', 'date')}{select('status', 'Davomat', statusOptions.attendance)}{select('homework_status', 'Vazifa', statusOptions.homework)}{input('homework_note', 'Vazifa izohi')}</div>;
  if (entity === 'salaries') return <div className="formGrid">{select('teacher', "O'qituvchi", data.teachers.map((t) => ({ value: t.id, label: t.full_name })))}{input('month', 'Oy', 'date')}{input('teaching_hours', 'Soatlar', 'number')}{input('hourly_rate', 'Stavka', 'number')}{input('bonus', 'Bonus', 'number')}{input('deductions', 'Ushlab qolish', 'number')}{checkbox('is_paid', "To'langan")}</div>;
  return <div className="formGrid">{input('name', 'Markaz nomi')}{input('email', 'Email', 'email')}{input('phone', 'Telefon')}{input('address', 'Manzil')}{input('currency', 'Valyuta')}{input('default_tuition_fee', "Standart to'lov", 'number')}</div>;
}

function validateRequired(entity: EntityKey, form: Record<string, string | boolean>) {
  if (entity === 'groups') {
    if (!String(form.name || '').trim()) return "Guruh nomini kiriting.";
    if (!String(form.level || '').trim()) return "Guruh darajasini kiriting.";
    const hasSchedule = days.some((day) => Boolean(form[`schedule_${day.value}_enabled`]));
    if (!hasSchedule) return "Kamida bitta dars kunini tanlang.";
  }
  if (entity === 'teachers') {
    if (!String(form.first_name || '').trim()) return "O'qituvchi ismini kiriting.";
    if (!String(form.email || '').trim()) return "O'qituvchi emailini kiriting.";
    if (!String(form.phone || '').trim()) return "O'qituvchi telefonini kiriting.";
    if (!form.user && !String(form.username || '').trim()) return "Kabinet loginini kiriting.";
    if (!form.user && !String(form.password || '').trim()) return "Kabinet parolini kiriting.";
  }
  if (entity === 'students') {
    if (!String(form.first_name || '').trim()) return "O'quvchi ismini kiriting.";
    if (!String(form.phone || '').trim()) return "O'quvchi telefonini kiriting.";
  }
  return '';
}

function buildInitial(entity: EntityKey, record: Record<string, unknown> | null): Record<string, string | boolean> {
  if (record) {
    const base = Object.fromEntries(Object.entries(record).map(([key, value]) => [key, typeof value === 'boolean' ? value : String(value ?? '')]));
    if (entity === 'groups') {
      return applyScheduleInitial(base, record.schedules as GroupSchedule[] | undefined, record);
    }
    if (entity === 'teachers') {
      const assigned = new Set((record.assigned_groups as number[] | undefined)?.map(String) || []);
      assigned.forEach((groupId) => {
        base[`teacher_group_${groupId}`] = true;
      });
    }
    return base;
  }
  const commonDate = today();
  const map: Record<EntityKey, Record<string, string | boolean>> = {
    teachers: { first_name: '', last_name: '', email: '', phone: '', hire_date: commonDate, hourly_rate: '0', status: 'active', username: '', password: '' },
    students: { first_name: '', last_name: '', phone: '', parent_phone: '', group: '', enrollment_date: commonDate, status: 'active' },
    groups: applyScheduleInitial({ name: '', level: '', day_of_week: 'monday', start_time: '18:00', end_time: '19:30', teacher: '', max_students: '20', tuition_fee: '0', is_active: true }, undefined),
    payments: { student: '', group: '', amount: '0', month: commonDate.slice(0, 8) + '01', status: 'pending', payment_method: 'cash' },
    attendances: { student: '', group: '', date: commonDate, status: 'present', homework_status: 'not_checked', homework_note: '' },
    salaries: { teacher: '', month: commonDate.slice(0, 8) + '01', teaching_hours: '0', hourly_rate: '0', bonus: '0', deductions: '0', is_paid: false },
    centers: { name: '', email: '', phone: '', address: '', currency: 'UZS', default_tuition_fee: '0' },
  };
  return map[entity];
}

function applyScheduleInitial(base: Record<string, string | boolean>, schedules?: GroupSchedule[], record?: Record<string, unknown>) {
  days.forEach((day) => {
    base[`schedule_${day.value}_enabled`] = false;
    base[`schedule_${day.value}_start`] = '18:00';
    base[`schedule_${day.value}_end`] = '19:30';
  });

  const scheduleList = schedules?.length
    ? schedules
    : record?.day_of_week
      ? [{ day_of_week: String(record.day_of_week), start_time: String(record.start_time || '18:00'), end_time: String(record.end_time || '19:30') }]
      : [{ day_of_week: 'monday', start_time: '18:00', end_time: '19:30' }];

  scheduleList.forEach((schedule) => {
    base[`schedule_${schedule.day_of_week}_enabled`] = true;
    base[`schedule_${schedule.day_of_week}_start`] = String(schedule.start_time).slice(0, 5);
    base[`schedule_${schedule.day_of_week}_end`] = String(schedule.end_time).slice(0, 5);
  });
  return base;
}

function buildPayload(entity: EntityKey, form: Record<string, string | boolean>) {
  const payload: Record<string, string | number | boolean | null | GroupSchedule[] | number[]> = {};

  payloadFields[entity].forEach((key) => {
    const value = form[key];
    if (value === undefined) return;
    if (value === '') {
      payload[key] = ['teacher', 'group', 'student'].includes(key) ? null : '';
      return;
    }
    payload[key] = value;
  });
  if (entity === 'groups') {
    const selectedSchedules = days
      .filter((day) => form[`schedule_${day.value}_enabled`])
      .map((day) => ({
        day_of_week: day.value,
        start_time: String(form[`schedule_${day.value}_start`] || '18:00'),
        end_time: String(form[`schedule_${day.value}_end`] || '19:30'),
      }));
    const firstSchedule = selectedSchedules[0] || { day_of_week: 'monday', start_time: '18:00', end_time: '19:30' };
    payload.schedules = selectedSchedules;
    payload.day_of_week = firstSchedule.day_of_week;
    payload.start_time = firstSchedule.start_time;
    payload.end_time = firstSchedule.end_time;
  }
  if (entity === 'teachers') {
    payload.assigned_groups = Object.entries(form)
      .filter(([key, value]) => key.startsWith('teacher_group_') && Boolean(value))
      .map(([key]) => Number(key.replace('teacher_group_', '')));
  }
  return payload;
}

const payloadFields: Record<EntityKey, string[]> = {
  teachers: ['first_name', 'last_name', 'email', 'phone', 'status', 'hourly_rate', 'hire_date', 'username', 'password'],
  students: ['first_name', 'last_name', 'phone', 'parent_phone', 'group', 'enrollment_date', 'status'],
  groups: ['name', 'level', 'teacher', 'max_students', 'tuition_fee', 'is_active'],
  payments: ['student', 'group', 'amount', 'month', 'status', 'payment_method'],
  attendances: ['student', 'group', 'date', 'status', 'homework_status', 'homework_note'],
  salaries: ['teacher', 'month', 'teaching_hours', 'hourly_rate', 'bonus', 'deductions', 'is_paid'],
  centers: ['name', 'email', 'phone', 'address', 'currency', 'default_tuition_fee'],
};

const days = [
  { value: 'monday', label: 'Dushanba' },
  { value: 'tuesday', label: 'Seshanba' },
  { value: 'wednesday', label: 'Chorshanba' },
  { value: 'thursday', label: 'Payshanba' },
  { value: 'friday', label: 'Juma' },
  { value: 'saturday', label: 'Shanba' },
  { value: 'sunday', label: 'Yakshanba' },
];

const statusOptions = {
  teacher: [{ value: 'active', label: 'Faol' }, { value: 'inactive', label: 'Nofaol' }, { value: 'leave', label: "Ta'tilda" }],
  student: [{ value: 'active', label: 'Faol' }, { value: 'inactive', label: 'Nofaol' }, { value: 'graduated', label: 'Bitirgan' }, { value: 'dropped', label: 'Ketgan' }],
  payment: [{ value: 'paid', label: "To'langan" }, { value: 'pending', label: 'Kutilmoqda' }, { value: 'overdue', label: "Muddati o'tgan" }, { value: 'partial', label: 'Qisman' }],
  attendance: [{ value: 'present', label: 'Kelgan' }, { value: 'absent', label: 'Kelmagan' }, { value: 'late', label: 'Kechikkan' }, { value: 'excused', label: 'Uzrli' }],
  homework: [{ value: 'not_checked', label: 'Vazifa: tekshirilmagan' }, { value: 'done', label: 'Vazifa: bajargan' }, { value: 'partial', label: 'Vazifa: qisman' }, { value: 'not_done', label: 'Vazifa: bajarmagan' }],
};

const paymentMethods = [
  { value: 'cash', label: 'Naqd' },
  { value: 'card', label: 'Karta' },
  { value: 'transfer', label: "O'tkazma" },
  { value: 'mobile', label: 'Mobil' },
  { value: 'other', label: 'Boshqa' },
];

function Groups({ groups, compact = false }: { groups: Group[]; compact?: boolean }) {
  return (
    <section className="tableCard">
      <div className="sectionHeader">
        <h2>Guruhlar</h2>
        <span>{groups.length} ta guruh</span>
      </div>
      <div className={compact ? 'groupCards compact' : 'groupCards'}>
        {groups.map((group) => (
          <article className="groupCard" key={group.id}>
            <div className="groupTop">
              <div>
                <h3>{group.name}</h3>
                <p>{group.teacher_name || "O'qituvchi biriktirilmagan"}</p>
              </div>
              <span>{group.level}</span>
            </div>
            <div className="groupMeta">
              <span>{group.schedule_display || 'Jadval kiritilmagan'}</span>
              <span>{group.students_count} o'quvchi</span>
              <span>{group.available_seats} joy</span>
            </div>
            <strong>{money(group.tuition_fee)}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function Payments({ payments, compact = false }: { payments: Payment[]; compact?: boolean }) {
  return (
    <section className="tableCard">
      <div className="sectionHeader">
        <h2>To'lovlar</h2>
        <span>{payments.length} ta yozuv</span>
      </div>
      <div className="table">
        {payments.map((payment) => (
          <div className="tableRow" key={payment.id}>
            <strong>{payment.student_name}</strong>
            {!compact && <span>{payment.group_name || '-'}</span>}
            <span>{money(payment.amount)}</span>
            <Badge value={payment.status} />
          </div>
        ))}
      </div>
    </section>
  );
}

function Badge({ value, ok }: { value: string; ok?: boolean }) {
  const status = value.toLowerCase();
  const tone = ok || status === 'paid' || status === 'active' || status === 'kelgan' || status === "to'langan" ? 'success' : status === 'overdue' || status === 'kelmagan' ? 'danger' : 'warning';
  return <span className={`badge ${tone}`}>{value}</span>;
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
