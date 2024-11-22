from flask import request, jsonify , redirect,url_for,render_template
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash

from models.models import *
from sqlalchemy import func
from config import app , db



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Empoyeer, int(user_id))
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Empoyeer.query.filter_by(login=username).first()
        if user and user.password == password:
            login_user(user)
            if user.role=="Администратор":
                return redirect(url_for("admin_dashboard"))
            elif user.role=="ОТК":
                return redirect(url_for("otk_dashboard"))
    return render_template("login.html")

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    return render_template("admin_dashboard.html")

#________________________________________________________ИП___________________________________________________________
@app.route("/ips")
@login_required
def list_ips():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    ips = Ip.query.all()
    return render_template("ips.html", ips=ips)

@app.route("/ips/add", methods=["POST"])
@login_required
def add_ip():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    ip_name = request.form.get("ip_name")
    if ip_name:
        new_ip = Ip(name=ip_name)
        db.session.add(new_ip)
        db.session.commit()
    return redirect(url_for("list_ips"))

@app.route("/ips/delete/<int:ip_id>")
@login_required
def delete_ip(ip_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    ip = Ip.query.get(ip_id)
    if ip:
        db.session.delete(ip)
        db.session.commit()
    return redirect(url_for("list_ips"))

@app.route("/ips/edit/<int:ip_id>", methods=["GET", "POST"])
@login_required
def edit_ip(ip_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    ip = Ip.query.get(ip_id)
    if not ip:
        return "ИП-шник не найден", 404
    
    if request.method == "POST":
        name = request.form.get("name")
        
        if name:
            ip.name = name
            db.session.commit()
            return redirect(url_for("list_ips"))
    
    return render_template("edit_ip.html", ip=ip)

#__________________________________________________________________ТОВАРЫ___________________________________________________
@app.route("/goods", methods=["GET", "POST"])
@login_required
def list_goods():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    ip_filter = request.args.get('ip_filter', None)

    query = Goods.query.join(Ip).filter(
        Goods.name.contains(search) | 
        Goods.barcode.contains(search) | 
        Goods.article.contains(search) | 
        Goods.wb_article.contains(search) | 
        Goods.country.contains(search) | 
        Goods.compound.contains(search) | 
        Goods.color.contains(search)
    )

    if ip_filter:
        query = query.filter(Goods.ip_id == ip_filter)

    if sort_order == 'asc':
        query = query.order_by(getattr(Goods, sort_by).asc())
    else:
        query = query.order_by(getattr(Goods, sort_by).desc())

    goods = query.all()
    ips = Ip.query.all()
    
    return render_template("goods.html", goods=goods, ips=ips, search=search, sort_by=sort_by, sort_order=sort_order, ip_filter=ip_filter)
@app.route("/goods/add",methods=["GET"])
@login_required
def  add_goods_page():
    ips = Ip.query.all()
    return  render_template("add_goods.html",ips=ips)
@app.route("/goods/add", methods=["POST"])
@login_required
def add_goods():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    ip_id = request.form.get("ip_id")
    name = request.form.get("name")
    barcode = request.form.get("barcode")
    article = request.form.get("article")
    wb_article = request.form.get("wb_article")
    country = request.form.get("country")
    compound = request.form.get("compound")
    color = request.form.get("color")
    
    if all([ip_id, name, barcode, article, wb_article, country, compound, color]):
        new_goods = Goods(
            ip_id=ip_id,
            name=name,
            barcode=barcode,
            article=article,
            wb_article=wb_article,
            country=country,
            compound=compound,
            color=color
        )
        db.session.add(new_goods)
        db.session.commit()
    return redirect(url_for("list_goods"))

@app.route("/goods/delete/<int:goods_id>")
@login_required
def delete_goods(goods_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    goods = Goods.query.get(goods_id)
    if goods:
        db.session.delete(goods)
        db.session.commit()
    return redirect(url_for("list_goods"))

@app.route("/employees/edit/<int:employee_id>", methods=["GET", "POST"])
@login_required
def edit_employee(employee_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    employee = Empoyeer.query.get(employee_id)
    if not employee:
        return "Сотрудник не найден", 404
    if request.method == "POST":
        employee.fio = request.form["fio"]
        employee.login = request.form["login"]
        employee.role = request.form["role"]
        if request.form["password"]:
            employee.password = request.form["password"]
        db.session.commit()
        flash("Сотрудник успешно отредактирован", "success")
        return redirect(url_for("list_employees"))
    return render_template("edit_employees.html", employee=employee)

@app.route("/goods/edit/<int:goods_id>", methods=["GET", "POST"])
@login_required
def edit_goods(goods_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    # Получаем товар по ID
    goods = Goods.query.get_or_404(goods_id)
    
    # Получаем список всех ИП для выпадающего списка
    ips = Ip.query.all()
    
    if request.method == "POST":
        try:
            # Обновляем данные товара
            goods.ip_id = request.form.get("ip_id")
            goods.name = request.form.get("name")
            goods.barcode = request.form.get("barcode")
            goods.article = request.form.get("article")
            goods.wb_article = request.form.get("wb_article")
            goods.country = request.form.get("country")
            goods.compound = request.form.get("compound")
            goods.color = request.form.get("color")
            
            # Обновляем дату редактирования
            goods.edit_date = datetime.utcnow()
            
            # Сохраняем изменения
            db.session.commit()
            
            flash("Товар успешно обновлен", "success")
            return redirect(url_for("list_goods"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при обновлении товара: {str(e)}", "error")
            return render_template("edit_goods.html", goods=goods, ips=ips)
    
    # Для GET запроса просто показываем форму
    return render_template("edit_goods.html", goods=goods, ips=ips)

#______________________________________________________________________________________СООТРУДНИКИ_________________________________________
@app.route("/employees/add", methods=["GET"])
@login_required
def add_employees_page():
    return render_template("add_employees.html")

@app.route("/employees/add", methods=["POST"])
@login_required
def add_employee():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    fio = request.form["fio"]
    login = request.form["login"]
    password = request.form["password"]
    role = request.form["role"]
    employee = Empoyeer(fio=fio, login=login, password=password, role=role)
    db.session.add(employee)
    db.session.commit()
    flash("Сотрудник успешно добавлен", "success")
    return redirect(url_for("list_employees"))

@app.route("/employees", methods=["GET", "POST"])
@login_required
def list_employees():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403

    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    query = Empoyeer.query.filter(
        Empoyeer.login.contains(search) |  # Заменили username на login
        Empoyeer.fio.contains(search) |    # Добавил поиск по ФИО
        Empoyeer.role.contains(search)
    )

    if sort_order == 'asc':
        query = query.order_by(getattr(Empoyeer, sort_by).asc())
    else:
        query = query.order_by(getattr(Empoyeer, sort_by).desc())

    employees = query.all()

    return render_template("employees.html", employees=employees, search=search, sort_by=sort_by, sort_order=sort_order)
  

@app.route("/employees/delete/<int:employee_id>")
@login_required
def delete_employee(employee_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    employee = Empoyeer.query.get(employee_id)
    if employee:
        db.session.delete(employee)
        db.session.commit()
    return redirect(url_for("list_employees"))





@app.route("/projects", methods=["GET", "POST"])
@login_required
def list_projects():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    query = Project.query.filter(
        Project.id.contains(search)
    )

    if sort_order == 'asc':
        query = query.order_by(getattr(Project, sort_by).asc())
    else:
        query = query.order_by(getattr(Project, sort_by).desc())

    projects = query.all()
    
    return render_template("projects.html", projects=projects, search=search, sort_by=sort_by, sort_order=sort_order)

@app.route("/projects/add")
@login_required
def add_project():
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    # Базовое название для нового проекта
    base_name = "Новый проект"
    
    # Получаем все проекты, начинающиеся с "Новый проект"
    existing_projects = Project.query.filter(
        Project.name.like(f"{base_name}%")
    ).all()
    
    if not existing_projects:
        # Если нет проектов с таким названием, используем базовое название
        new_name = base_name
    else:
        # Получаем список номеров существующих проектов
        existing_numbers = []
        for project in existing_projects:
            if project.name == base_name:
                existing_numbers.append(0)
            else:
                # Пытаемся получить номер из названия (например, "Новый проект 1" -> 1)
                try:
                    num = int(project.name.replace(f"{base_name} ", ""))
                    existing_numbers.append(num)
                except ValueError:
                    continue
        
        # Находим первое свободное число
        next_number = 1
        while next_number in existing_numbers:
            next_number += 1
            
        # Формируем новое имя
        new_name = f"{base_name} {next_number}" if next_number > 0 else base_name
    
    try:
        # Создаем новый проект
        new_project = Project(name=new_name)
        db.session.add(new_project)
        db.session.commit()
        flash(f'Проект "{new_name}" успешно создан', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при создании проекта: {str(e)}', 'error')
    
    return redirect(url_for('list_projects'))
@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    goods = Goods.query.all()
    
    if not project:
        return "Проект не найден", 404
    
    if request.method == "POST":
        create_date = request.form.get("create_date")
        total_quantity = request.form.get("quantity")
        goods_id = request.form.get("goods_id")
        
        if all([create_date, total_quantity, goods_id]):
            create_date = datetime.strptime(create_date, "%Y-%m-%d")
            project.create_date = create_date
            project.quantity = total_quantity
            project.goods_id = goods_id
            db.session.commit()
            return redirect(url_for("list_projects"))
    
    return render_template("edit_project.html", project=project, goods=goods)

@app.route("/projects/<int:project_id>/delete")
@login_required
def delete_project(project_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for("list_projects"))

@app.route("/projects/<int:project_id>/receptions")
@login_required
def project_receptions(project_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    receptions = Reception.query.filter_by(project_id=project_id).all()
    
    if not project:
        return "Проект не найден", 404
    
    return render_template("project_receptions.html", project=project, receptions=receptions)

"""@app.route("/projects/<int:project_id>/receptions/add", methods=["GET", "POST"])
@login_required
def add_reception(project_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    employees = Empoyeer.query.all()
    
    if not project:
        return "Проект не найден", 404
    
    if request.method == "POST":
        name_act = request.form.get("name_action")
        
        
        if all([name_act]):
            new_reception = Reception(
                name = name_act,
                
                project_id=project_id
            )
            db.session.add(new_reception)
            db.session.commit()
            return redirect(url_for("project_receptions", project_id=project_id))
    
    return render_template("add_reception.html", project=project, employees=employees)
"""
@app.route("/projects/<int:project_id>/receptions/<int:reception_id>/edit", methods=["GET", "POST"])
@login_required
def edit_reception(project_id, reception_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    reception = Reception.query.get(reception_id)
    employees = Empoyeer.query.all()
    
    if not project or not reception:
        return "Проект или действие не найдены", 404
    
    if request.method == "POST":
        goods_quantity = request.form.get("goods_quantity")
        employee_id = request.form.get("employee_id")
        
        if all([goods_quantity, employee_id]):
            reception.goods_quantity = goods_quantity
            reception.employee_id = employee_id
            db.session.commit()
            return redirect(url_for("project_receptions", project_id=project_id))
    
    return render_template("edit_reception.html", project=project, reception=reception, employees=employees)

@app.route("/projects/<int:project_id>/receptions/<int:reception_id>/delete")
@login_required
def delete_reception(project_id, reception_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    reception = Reception.query.get(reception_id)
    
    if not project or not reception:
        return "Проект или действие не найдены", 404
    
    db.session.delete(reception)
    db.session.commit()
    return redirect(url_for("project_receptions", project_id=project_id))

@app.route('/take_reception/<int:reception_id>', methods=['POST'])
@login_required
def take_reception(reception_id):
    reception = Reception.query .get(reception_id)
    taken_quantity = int(request.form['taken_quantity'])
    if taken_quantity <= reception.action.project.total_quantity:
        reception.taken_quantity += taken_quantity
        db.session.commit()
        return redirect(url_for('employee_receptions'))
    else:
        return 'Недостаточно товара для выполнения действия'



@app.route('/complete_reception/<int:reception_id>')
@login_required
def complete_reception(reception_id):
    reception = Reception.query.get(reception_id)
    reception.status = 'Выполнено'
    db.session.commit()
    return redirect(url_for('employee_receptions'))


@app.route("/projects/<int:project_id>/actions", methods=["GET", "POST"])
@login_required
def project_actions(project_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    project = Project.query.get(project_id)
    if not project:
        return "Проект не найден", 404
    
    if request.method == "POST":
        name = request.form.get("name")
        quantity = request.form.get("quantity")
        
        if all([name, quantity]):
            new_action = Action(
                name=name,
                project_id=project_id,
                quantity=quantity
            )
            db.session.add(new_action)
            db.session.commit()
            return redirect(url_for("project_actions", project_id=project_id))
    
    actions = Action.query.filter_by(project_id=project_id).all()
    
    return render_template("project_actions.html", project=project, actions=actions)

@app.route("/projects/<int:project_id>/actions/<int:action_id>/complete", methods=["POST"])
@login_required
def complete_action(project_id, action_id):
    if current_user.role != "Администратор":
        return "Доступ запрещен", 403
    
    action = Action.query.get(action_id)
    if not action:
        return "Действие не найдено", 404
    
    action.completed_quantity += 1
    db.session.commit()
    return redirect(url_for("project_actions", project_id=project_id))
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


from collections import defaultdict
from datetime import datetime


@app.route('/projects/<int:project_id>')
def project_details(project_id):
    project = Project.query.get_or_404(project_id)

    # Получаем все приемки проекта
    receptions = db.session.query(Reception).\
        join(ProjectReception).\
        filter(ProjectReception.project_id == project_id).\
        order_by(Reception.priemka_date).all()

    # Для каждой приемки получаем связанные действия и пользователей
    for reception in receptions:
        # Подсчитываем общее количество товаров в приемке
        reception.total_quantity = db.session.query(func.sum(GoodsReception.kol_vo)).\
            filter(GoodsReception.priemka_id == reception.id).\
            scalar() or 0

        # Получаем действия для приемки
        reception.actions = db.session.query(Action).\
            join(ReceptionAction, ReceptionAction.deistvie_id == Action.id).\
            filter(ReceptionAction.priemka_id == reception.id).\
            all()
        
        # Для каждого действия получаем информацию о пользователях и считаем общее количество
        for action in reception.actions:
            # Получаем пользовательские действия и информацию о пользователях
            user_actions_query = db.session.query(
                UserAction, 
                Empoyeer
            ).join(
                Empoyeer, 
                UserAction.user_id == Empoyeer.id
            ).filter(
                UserAction.deistvie_id == action.id
            ).all()

            # Сохраняем данные в виде списка кортежей
            action.user_action_data = user_actions_query

            # Подсчет общего количества обработанных единиц для действия
            action.total_processed = db.session.query(func.sum(UserAction.kol_vo)).\
                filter(UserAction.deistvie_id == action.id).\
                scalar() or 0

            # Используем общее количество товаров в приемке для расчета прогресса
            action.quantity = reception.total_quantity
            # Вычисление процента выполнения
            action.progress_percentage = (action.total_processed / action.quantity * 100) \
                if action.quantity > 0 else 0

    # Получаем даты приемок
    dates = [reception.priemka_date for reception in receptions]

    # Получаем все товары для каждой приемки
    goods_by_id = defaultdict(lambda: {
        'name': '',
        'color': '',
        'size': '',
        'barcode': '',
        'receptions': defaultdict(lambda: {'quantity': 0, 'defect': 0})
    })

    for reception in receptions:
        goods_data = db.session.query(
            Goods.id, 
            Goods.name, 
            Goods.color, 
            Goods.size, 
            Goods.barcode,
            GoodsReception.kol_vo,
            func.coalesce(func.sum(Defect.kol_vo), 0).label('defect_quantity')
        ).select_from(Goods).\
        join(GoodsReception, Goods.id == GoodsReception.tovar_id).\
        outerjoin(Defect, (Defect.tovar_id == Goods.id) & (Defect.priemka_id == reception.id)).\
        filter(GoodsReception.priemka_id == reception.id).\
        group_by(Goods.id, Goods.name, Goods.color, Goods.size, Goods.barcode, GoodsReception.kol_vo).\
        all()

        for good_id, name, color, size, barcode, quantity, defect_quantity in goods_data:
            goods_by_id[good_id]['name'] = name
            goods_by_id[good_id]['color'] = color
            goods_by_id[good_id]['size'] = size
            goods_by_id[good_id]['barcode'] = barcode
            goods_by_id[good_id]['receptions'][reception.priemka_date] = {
                'quantity': quantity,
                'defect': defect_quantity
            }

    return render_template('project_details.html',
                         project=project,
                         goods=goods_by_id,
                         dates=dates,
                         receptions=receptions)


from flask import request, jsonify

@app.route('/projects/<int:project_id>/update_name', methods=['POST'])
@login_required
def update_project_name(project_id):
    if current_user.role != "Администратор":
        return jsonify({"success": False, "message": "Доступ запрещен"}), 403
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"success": False, "message": "Проект не найден"}), 404
    
    new_name = request.json.get('name')
    if not new_name:
        return jsonify({"success": False, "message": "Имя проекта не может быть пустым"}), 400
    
    project.name = new_name
    db.session.commit()
    
    return jsonify({"success": True, "message": "Название проекта обновлено"})

@app.route('/projects/<int:project_id>/select_goods', methods=['GET'])
@login_required
def select_goods(project_id):
    project = Project.query.get_or_404(project_id)
    all_goods = Goods.query.all()
    return render_template('select_goods.html', project=project, all_goods=all_goods)

@app.route('/projects/<int:project_id>/add_new_goods', methods=['GET', 'POST'])
@login_required
def add_new_goods(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        ip_id = request.form.get('ip_id')
        name = request.form.get('name')
        article = request.form.get('article')
        wb_article = request.form.get('wb_article')
        country = request.form.get('country')
        compound = request.form.get('compound')
        color = request.form.get('color')
        sizes = request.form.getlist('sizes[]')
        barcodes = request.form.getlist('barcodes[]')

        for size, barcode in zip(sizes, barcodes):
            new_goods = Goods(
                ip_id=ip_id,
                name=name,
                article=article,
                wb_article=wb_article,
                country=country,
                compound=compound,
                color=color,
                size=size,
                barcode=barcode
            )
            db.session.add(new_goods)
        db.session.commit()

        return redirect(url_for('select_goods', project_id=project_id))
    return render_template('add_new_goods.html', project=project, ips=Ip.query.all())

from sqlalchemy import desc
import json

@app.route('/projects/<int:project_id>/add_goods', methods=['POST'])
@login_required
def add_goods_to_project(project_id):
    project = Project.query.get_or_404(project_id)
    goods_ids = json.loads(request.form.get('goods_ids'))  # Получаем список ID товаров
    print(goods_ids)

    # Найдем последний приход для данного проекта
    last_reception = Reception.query.join(ProjectReception).filter(
        ProjectReception.project_id == project_id
    ).order_by(desc(Reception.priemka_date)).first()

    if last_reception:
        # Добавляем товары к последнему приходу с количеством 0
        for goods_id in goods_ids:
            reception_goods = GoodsReception(
                priemka_id=last_reception.id,
                tovar_id=goods_id,
                kol_vo=0
            )
            db.session.add(reception_goods)
    else:
        # Если приходов для проекта нет, создаем новый
        new_reception = Reception(priemka_date=datetime.now())
        db.session.add(new_reception)
        db.session.commit()

        # Добавляем товары к новому приходу с количеством 0
        for goods_id in goods_ids:
            reception_goods = GoodsReception(
                priemka_id=new_reception.id,
                tovar_id=goods_id,
                kol_vo=0
            )
            db.session.add(reception_goods)

    db.session.commit()  # Коммитим все изменения за один раз
    return jsonify({'success': True})
@app.route('/search_goods')
@login_required
def search_goods():
    query = request.args.get('query', '')
    goods = Goods.query.filter(
        (Goods.name.ilike(f'%{query}%')) |
        (Goods.color.ilike(f'%{query}%')) |
        (Goods.size.ilike(f'%{query}%')) |
        (Goods.barcode.ilike(f'%{query}%'))
    ).all()
    return jsonify([{'id': g.id, 'name': g.name, 'color': g.color, 'size': g.size, 'barcode': g.barcode} for g in goods])

@app.route('/update_project_detail', methods=['POST'])
@login_required
def update_project_detail():
    data = request.json
    project_id = data.get('project_id')
    good_id = data.get('good_id')
    date = data.get('date')
    field = data.get('field')
    value = data.get('value')
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"success": False, "message": "Project not found"}), 404

    reception = Reception.query.join(ProjectReception).filter(
        ProjectReception.project_id == project_id,
        Reception.priemka_date == date
    ).first()
    
    if not reception:
        return jsonify({"success": False, "message": "Reception not found"}), 405

    goods_reception = GoodsReception.query.filter_by(
        priemka_id=reception.id,
        tovar_id=good_id
    ).first()

    if not goods_reception:
        goods_reception = GoodsReception(priemka_id=reception.id, tovar_id=good_id)
        db.session.add(goods_reception)

    if field == 'quantity':
        goods_reception.kol_vo = int(value)
    elif field == 'defect':
        defect = Defect.query.filter_by(
            priemka_id=reception.id,
            tovar_id=good_id
        ).first()
        if not defect:
            defect = Defect(priemka_id=reception.id, tovar_id=good_id)
            db.session.add(defect)
        defect.kol_vo = int(value)
    else:
        return jsonify({"success": False, "message": "Invalid field"}), 400

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Data updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

from flask import request, jsonify

@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    data = request.json
    project_id = data.get('project_id')
    goods_id = data.get('goods_id')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d')
    quantity = data.get('quantity')

    reception = Reception.query.join(ProjectReception).filter(
        ProjectReception.project_id == project_id,
        Reception.priemka_date == date
    ).first()

    if not reception:
        return jsonify({"success": False, "message": "Reception not found"}), 404

    goods_reception = GoodsReception.query.filter_by(
        priemka_id=reception.id,
        tovar_id=goods_id
    ).first()

    if goods_reception:
        goods_reception.kol_vo = quantity
    else:
        goods_reception = GoodsReception(
            priemka_id=reception.id,
            tovar_id=goods_id,
            kol_vo=quantity
        )
        db.session.add(goods_reception)

    db.session.commit()

    return jsonify({"success": True, "message": "Quantity updated successfully"}), 200

@app.route('/projects/<int:project_id>/delete_good/<int:good_id>', methods=['POST'])
@login_required
def delete_good_from_project(project_id, good_id):
    if current_user.role != "Администратор":
        return jsonify({"success": False, "message": "Доступ запрещен"}), 403

    # Здесь логика удаления товара из проекта
    # Например:
    GoodsReception.query.filter_by(tovar_id=good_id).delete()
    db.session.commit()

    return jsonify({"success": True, "message": "Товар успешно удален из проекта"})

from sqlalchemy import and_

@app.route('/projects/<int:project_id>/delete_reception/<date>', methods=['POST'])
@login_required
def delete_reception_from_project(project_id, date):
    if current_user.role != "Администратор":
        return jsonify({"success": False, "message": "Доступ запрещен"}), 403

    try:
        reception_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Найдем нужную приемку
        reception = Reception.query.join(ProjectReception).filter(
            and_(
                ProjectReception.project_id == project_id,
                Reception.priemka_date == reception_date
            )
        ).first()

        if reception:
            # Удаляем связанные записи
            GoodsReception.query.filter_by(priemka_id=reception.id).delete()
            ProjectReception.query.filter_by(priemka_id=reception.id).delete()
            
            # Удаляем саму приемку
            db.session.delete(reception)
            db.session.commit()
            return jsonify({"success": True, "message": "Приход успешно удален"})
        else:
            return jsonify({"success": False, "message": "Приход не найден"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    


from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

@app.route('/projects/<int:project_id>/add_reception', methods=['GET', 'POST'])
@login_required
def add_reception(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        priemka_date_str = request.form.get('priemka_date')
        try:
            priemka_date = datetime.strptime(priemka_date_str, '%Y-%m-%d').date()
            
            # Создаем новую приемку
            new_reception = Reception(priemka_date=priemka_date)
            db.session.add(new_reception)
            db.session.flush()  # Это присвоит ID новой приемке
            
            # Создаем связь между проектом и приемкой
            project_reception = ProjectReception(project_id=project.id, priemka_id=new_reception.id)
            db.session.add(project_reception)
            
            # Получаем все товары, связанные с проектом
            project_goods = Goods.query.join(GoodsReception).join(Reception).join(ProjectReception).filter(ProjectReception.project_id == project.id).distinct().all()
            
            # Добавляем каждый товар в новую приемку с количеством 0
            for good in project_goods:
                goods_reception = GoodsReception(
                    priemka_id=new_reception.id,
                    tovar_id=good.id,
                    kol_vo=0  # Устанавливаем количество 0
                )
                db.session.add(goods_reception)
            
            db.session.commit()
            flash('Новая приемка успешно добавлена и привязана к проекту', 'success')
            return redirect(url_for('project_details', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении приемки: {str(e)}', 'error')

    return render_template('add_reception.html', project=project)
@app.route('/projects/<int:project_id>/receptions/<int:reception_id>/actions', methods=['GET'])
@login_required
def reception_actions(project_id, reception_id):
    reception = Reception.query.get_or_404(reception_id)
    project = Project.query.get_or_404(project_id)
    
    # Получаем все действия для данной приемки
    reception_actions = db.session.query(
        Action,
        ReceptionAction,
        UserAction
    ).join(
        ReceptionAction,
        ReceptionAction.deistvie_id == Action.id
    ).outerjoin(
        UserAction,
        UserAction.deistvie_id == Action.id
    ).filter(
        ReceptionAction.priemka_id == reception_id
    ).all()
    
    # Получаем информацию о сотрудниках
    employees = Empoyeer.query.all()
    
    return render_template(
        'reception_actions.html',
        reception=reception,
        project=project,
        reception_actions=reception_actions,
        employees=employees
    )

@app.route('/projects/<int:project_id>/receptions/<int:reception_id>/actions/add', methods=['POST', 'GET'])
@login_required
def add_reception_action(project_id, reception_id):
    if request.method == 'POST':
        # Получаем выбранные стандартные действия
        selected_actions = request.form.getlist('actions')
        
        # Получаем пользовательское действие, если оно есть
        custom_action = request.form.get('custom_action')
        if custom_action and custom_action.strip():
            selected_actions.append(custom_action.strip())

        try:
            for action_name in selected_actions:
                # Создаем новое действие
                new_action = Action(
                    name=action_name,
                    status='Активно'  # Начальный статус
                )
                db.session.add(new_action)
                db.session.flush()  # Чтобы получить id нового действия

                # Создаем связь с приемкой
                reception_action = ReceptionAction(
                    priemka_id=reception_id,
                    deistvie_id=new_action.id
                )
                db.session.add(reception_action)

            db.session.commit()
            flash('Действия успешно добавлены', 'success')
            return redirect(url_for('project_details', project_id=project_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении действий: {str(e)}', 'error')
            return redirect(url_for('project_details', project_id=project_id))

    # Для GET запроса показываем форму
    return render_template(
        'add_reception_action.html',
        project_id=project_id,
        reception_id=reception_id
    )

@app.route('/reception-actions/<int:action_id>/take', methods=['POST'])
@login_required
def take_action(action_id):
    quantity = int(request.form.get('quantity', 0))
    status = request.form.get('status', 'В работе')
    
    # Создаем запись о взятии действия сотрудником
    new_user_action = UserAction(
        deistvie_id=action_id,
        user_id=current_user.id,
        kol_vo=quantity,
        status=status
    )
    db.session.add(new_user_action)
    db.session.commit()
    
    return redirect(request.referrer)


#OTK

@app.route('/otk_dashboard')
@login_required
def otk_dashboard():
    # Проверка роли текущего пользователя
    if current_user.role != "ОТК":
        return "Доступ запрещен", 403

    # Получаем все активные проекты
    projects = Project.query.all()

    # Получаем текущие задачи сотрудника с загрузкой связанных данных
    tasks_data = db.session.query(
        UserAction,
        Action,
        Reception,
        Project
    ).join(
        Action, UserAction.deistvie_id == Action.id
    ).join(
        ReceptionAction, ReceptionAction.deistvie_id == Action.id
    ).join(
        Reception, Reception.id == ReceptionAction.priemka_id
    ).join(
        ProjectReception, ProjectReception.priemka_id == Reception.id
    ).join(
        Project, Project.id == ProjectReception.project_id
    ).filter(
        UserAction.user_id == current_user.id,
        UserAction.status == 'in work'
    ).all()
    
    # Преобразуем результаты в более удобную структуру и группируем по датам приемок
    current_receptions = {}
    for user_action, action, reception, project in tasks_data:
        reception_date = reception.priemka_date.strftime('%d.%m.%Y')
        if reception_date not in current_receptions:
            current_receptions[reception_date] = []
        current_receptions[reception_date].append({
            'user_action': user_action,
            'action': action,
            'reception': reception,
            'project': project
        })
    
    return render_template(
        'otk_dashboard.html',
        projects=projects,
        current_receptions=current_receptions
    )
@app.route('/otk_project_details/<int:project_id>')
@login_required
def otk_project_details(project_id):
    if current_user.role != "ОТК":
        return "Доступ запрещен", 403

    project = Project.query.get_or_404(project_id)
    
    # Получаем приемки через связующую таблицу
    receptions = Reception.query.join(ProjectReception).filter(
        ProjectReception.project_id == project_id
    ).all()
    
    # Для каждой приемки получаем общее количество товаров
    for reception in receptions:
        reception.total_quantity = db.session.query(func.sum(GoodsReception.kol_vo)).\
            filter(GoodsReception.priemka_id == reception.id).\
            scalar() or 0
            
        # Получаем действия для приемки
        reception.actions = db.session.query(Action).\
            join(ReceptionAction, ReceptionAction.deistvie_id == Action.id).\
            filter(ReceptionAction.priemka_id == reception.id).\
            all()
            
        # Для каждого действия получаем количество уже взятых товаров
        for action in reception.actions:
            action.taken_quantity = db.session.query(func.sum(UserAction.kol_vo)).\
                filter(UserAction.deistvie_id == action.id).\
                scalar() or 0
            
            # Вычисляем оставшееся доступное количество
            action.available_quantity = reception.total_quantity - action.taken_quantity

    return render_template(
        'otk_project_details.html',
        project=project,
        receptions=receptions
    )

@app.route('/take_tasks', methods=['POST'])
@login_required
def take_tasks():
    if current_user.role != "ОТК":
        return "Доступ запрещен", 403

    actions_ids = request.form.getlist('actions[]')  # Получаем массив ID действий
    total_quantities = {int(k.split('_')[-1]): request.form.get(k, type=int) for k in request.form if k.startswith('total_quantity_')}  # Получаем общее количество товаров для каждой приемки

    # Проверяем, есть ли у пользователя уже начатые задачи
    active_tasks = UserAction.query.filter_by(user_id=current_user.id, status='in work').all()
    if active_tasks:
        flash("Вы не можете взять новую задачу, пока не завершите уже начатые.")
        return redirect(url_for('otk_dashboard'))

    # Проверяем, что выбраны действия и общее количество указано
    if not actions_ids or not total_quantities:
        flash("Выберите хотя бы одно действие и укажите количество.")
        return redirect(url_for('otk_dashboard'))

    for action_id in actions_ids:
        action = Action.query.get_or_404(action_id)

        # Получаем связанную приемку через ReceptionAction
        reception_action = ReceptionAction.query.filter_by(deistvie_id=action_id).first()
        if not reception_action:
            print(f"Действие {action.name} не привязано к приемке")
            continue

        reception = Reception.query.get(reception_action.priemka_id)

        # Получаем общее количество товаров в приемке
        total_available_quantity = db.session.query(func.sum(GoodsReception.kol_vo)).\
            filter(GoodsReception.priemka_id == reception.id).\
            scalar() or 0

        # Получаем уже взятое количество для этого действия
        taken_quantity = db.session.query(func.sum(UserAction.kol_vo)).\
            filter(UserAction.deistvie_id == action_id).\
            scalar() or 0

        # Проверяем доступное количество
        available_quantity = total_available_quantity - taken_quantity

        # Получаем общее количество для текущей приемки
        current_total_quantity = total_quantities.get(reception.id, 0)

        if current_total_quantity > available_quantity:
            print(f"Нельзя взять больше доступного количества ({available_quantity}) для действия {action.name}")
            continue

        # Создаем новую запись о задаче
        user_action = UserAction(
            user_id=current_user.id,
            deistvie_id=action_id,
            kol_vo=current_total_quantity,  # Используем общее количество для текущей приемки
            status='in work'  # Устанавливаем статус в "в работе"
        )
        db.session.add(user_action)

    try:
        db.session.commit()
        flash("Задачи успешно взяты")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при взятии задачи: {str(e)}")

    return redirect(url_for('otk_dashboard'))

@app.route('/complete_task', methods=['POST'])
@login_required
def complete_task():
    if current_user.role != "ОТК":
        return "Доступ запрещен", 403
        
    task_ids = request.form.getlist('task_ids[]')  # Получаем массив ID задач

    for task_id in task_ids:
        user_action = UserAction.query.get_or_404(task_id)
        
        # Получаем приемку через связи
        reception = Reception.query.join(ReceptionAction).filter(
            ReceptionAction.deistvie_id == user_action.deistvie_id
        ).first()
        
        if not reception:
            flash(f"Ошибка: не найдена связанная приемка для задачи {task_id}")
            continue
        
        # Здесь вы можете добавить логику для учета брака, если это необходимо
        # Например, если у вас есть возможность вводить брак для каждой задачи
        # Но в текущем запросе это убрано

        # Обновляем статус действия
        user_action.status = 'ended'
    
    try:
        db.session.commit()
        flash("Выбранные задачи успешно завершены")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при сохранении данных: {str(e)}")
    
    return redirect(url_for('otk_dashboard'))

@app.route('/projects/<int:project_id>/actions/<int:action_id>/delete', methods=['POST'])
@login_required
def delete_action(project_id, action_id):
    try:
        # Получаем действие
        action = Action.query.get_or_404(action_id)
        
        # Удаляем связанные записи из таблицы user_actions
        UserAction.query.filter_by(deistvie_id=action_id).delete()
        
        # Удаляем связи из таблицы reception_actions
        ReceptionAction.query.filter_by(deistvie_id=action_id).delete()
        
        # Удаляем само действие
        db.session.delete(action)
        db.session.commit()
        
        flash('Действие успешно удалено', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении действия: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/report_defect/<int:reception_id>', methods=['GET', 'POST'])
@login_required
def report_defect(reception_id):
    # Проверка роли текущего пользователя
    if current_user.role != "ОТК":
        return "Доступ запрещен", 403

    # Получаем приемку по ID
    reception = Reception.query.get_or_404(reception_id)
    
    # Получаем товары, связанные с этой приемкой
    products = db.session.query(Goods).join(GoodsReception).filter(GoodsReception.priemka_id == reception.id).all()

    if request.method == 'POST':
        # Обработка данных о браке
        for product in products:
            defect_quantity = request.form.get(f'defect_quantity_{product.id}', type=int) or 0
            if defect_quantity > 0:
                # Здесь добавьте логику для суммирования брака
                defect_record = Defect.query.filter_by(tovar_id=product.id, priemka_id=reception.id).first()
                if defect_record:
                    defect_record.kol_vo += defect_quantity
                else:
                    new_defect = Defect(tovar_id=product.id, priemka_id=reception.id, kol_vo=defect_quantity)
                    db.session.add(new_defect)

        db.session.commit()
        return redirect(url_for('otk_dashboard'))

    return render_template('report_defect.html', reception=reception, products=products)
if __name__ == "__main__":
    app.run()